from unittest.mock import Mock, patch

import pytest
from flask.testing import FlaskClient
from flask_restx import ValidationError

from app.api.sites import get_geolocation_filter
from app.models import GeolocationFilter, SiteType
from app.services.sites import get_available_sites, get_playtomic_sites


class TestAvailableSites:
    def test_get_returns_response(self, client: FlaskClient, playtomic_site, mocker) -> None:
        mocker.patch("app.services.sites.get_playtomic_sites", return_value=[playtomic_site])
        response = client.get("/api/available-sites/")
        json_data = response.get_json()
        expected_response = get_available_sites().model_dump()

        assert all(
            site["name"] == expected_site["name"]
            for site, expected_site in zip(json_data["sites"], expected_response["sites"])
        )
        playtomic_sites = [site for site in json_data["sites"] if site["type"] == "playtomic"]
        assert len(playtomic_sites) == 1
        assert json_data["last_update"] == expected_response["last_update"]

    def test_get_returns_response_filtered_by_geolocation(self, client: FlaskClient) -> None:
        response = client.get("/api/available-sites/?latitude=39.5082456&longitude=-0.3612918&radius_km=1")
        json_data = response.get_json()
        sites = json_data["sites"]
        assert len(sites) == 1

        response = client.get("/api/available-sites/?latitude=39.5082456&longitude=-0.3612918&radius_km=10")
        json_data = response.get_json()
        sites = json_data["sites"]
        assert len(sites) == 3


class TestGeolocationFilter:
    def test_get_geolocation_filter_returns_none_when_no_args(self) -> None:
        assert get_geolocation_filter(None, None, None) is None

    def test_get_geolocation_filter_raises_validation_error_when_some_arg(self) -> None:
        with pytest.raises(ValidationError):
            get_geolocation_filter(1.0, None, None)
        with pytest.raises(ValidationError):
            get_geolocation_filter(None, 1.0, 1)

    def test_get_geolocation_filter_returns_geolocation_filter_when_all_args(self) -> None:
        result = get_geolocation_filter(1.1, -1.1, 1)
        assert result is not None
        assert result.latitude == 1.1
        assert result.longitude == -1.1
        assert result.radius_km == 1


class TestGetPlaytomicSites:
    @patch("app.services.availability.requests.get")
    def test_get_playtomic_sites_success(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = [
            {
                "tenant_name": "Playtomic Test Site",
                "tenant_uid": "club_padel",
                "tenant_id": "67890",
                "address": {"coordinate": {"lat": "40.416775", "lon": "-3.703790"}},
            }
        ]
        mock_get.return_value = mock_response

        geo_filter = GeolocationFilter(latitude=40.416775, longitude=-3.703790, radius_km=25)
        sites = get_playtomic_sites(geo_filter)

        assert len(sites) == 1
        assert sites[0].name == "Playtomic Test Site"
        assert sites[0].url == "https://playtomic.io/club_padel/67890"
        assert sites[0].coordinates == (40.416775, -3.70379)
        assert sites[0].type == SiteType.PLAYTOMIC

        args, kwargs = mock_get.call_args
        assert "coordinate=40.416775%2C-3.70379" in args[0]
        assert "radius=25000" in args[0]

    @patch("app.services.availability.requests.get")
    def test_get_playtomic_sites_default_filter(self, mock_get):
        mock_response = Mock()
        mock_response.json.return_value = []
        mock_get.return_value = mock_response

        sites = get_playtomic_sites()

        assert len(sites) == 0
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "coordinate=39.469908%2C-0.376288" in args[0]
        assert "radius=50000" in args[0]

    @patch("app.services.availability.requests.get")
    def test_get_playtomic_sites_error(self, mock_get):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        sites = get_playtomic_sites()

        assert len(sites) == 0
        mock_get.assert_called_once()
