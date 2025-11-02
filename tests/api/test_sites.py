from pytest import fixture

from app.models import GeolocationFilter
from app.services.sites import get_available_sites


class TestAvailableSites:
    @fixture
    def geo_filter(self) -> GeolocationFilter:
        return GeolocationFilter(latitude=40.416775, longitude=-3.703790, radius_km=25)

    def test_get_returns_response(self, mocker, client, geo_filter) -> None:
        response = client.get("/api/sites/", headers={"X-GEOLOCATION": "40.416775,-3.703790,25"})
        json_data = response.get_json()
        expected_response = get_available_sites(geo_filter).model_dump()

        assert all(
            site["name"] == expected_site["name"]
            for site, expected_site in zip(json_data["sites"], expected_response["sites"])
        )
        assert json_data["last_update"] == expected_response["last_update"]
