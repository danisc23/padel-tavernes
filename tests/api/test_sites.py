import pytest
from flask.testing import FlaskClient
from flask_restx import ValidationError

from app.api.sites import get_geolocation_filter
from app.services.sites import get_available_sites


class TestAvailableSites:
    def test_get_returns_response(self, client: FlaskClient) -> None:
        response = client.get("/api/available-sites/")
        json_data = response.get_json()
        expected_response = get_available_sites().model_dump()

        assert all(
            site["name"] == expected_site["name"]
            for site, expected_site in zip(json_data["sites"], expected_response["sites"])
        )
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
            get_geolocation_filter(None, 1.0, 1.0)

    def test_get_geolocation_filter_returns_geolocation_filter_when_all_args(self) -> None:
        result = get_geolocation_filter(1.1, -1.1, 1.2)
        assert result is not None
        assert result.latitude == 1.1
        assert result.longitude == -1.1
        assert result.radius_km == 1.2
