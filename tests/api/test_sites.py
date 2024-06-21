from unittest.mock import Mock, patch

from pytest import fixture

from app.models import GeolocationFilter, SiteType
from app.services.sites import get_available_sites, get_playtomic_sites


class TestAvailableSites:
    @fixture
    def geo_filter(self) -> GeolocationFilter:
        return GeolocationFilter(latitude=40.416775, longitude=-3.703790, radius_km=25)

    def test_get_returns_response(self, mocker, client, playtomic_site, geo_filter) -> None:
        mocker.patch("app.services.sites.get_playtomic_sites", return_value=[playtomic_site])
        response = client.get("/api/available-sites/", headers={"X-GEOLOCATION": "40.416775,-3.703790,25"})
        json_data = response.get_json()
        expected_response = get_available_sites(geo_filter).model_dump()

        assert all(
            site["name"] == expected_site["name"]
            for site, expected_site in zip(json_data["sites"], expected_response["sites"])
        )
        playtomic_sites = [site for site in json_data["sites"] if site["type"] == "playtomic"]
        assert len(playtomic_sites) == 1
        assert json_data["last_update"] == expected_response["last_update"]


class TestGetPlaytomicSites:
    @fixture
    def geo_filter(self) -> GeolocationFilter:
        return GeolocationFilter(latitude=40.416775, longitude=-3.703790, radius_km=25)

    @patch("app.services.availability.requests.get")
    def test_get_playtomic_sites_success(self, mock_get, geo_filter: GeolocationFilter):
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
    def test_get_playtomic_sites_error(self, mock_get, geo_filter: GeolocationFilter):
        mock_response = Mock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response

        sites = get_playtomic_sites(geo_filter)

        assert len(sites) == 0
        mock_get.assert_called_once()
