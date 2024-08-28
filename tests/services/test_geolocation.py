from unittest.mock import MagicMock

import pytest

from app.integrations.geolocation.geolocation_provider_interface import (
    GeolocationProvider,
)
from app.models import GeolocatedPlace
from app.services.geolocation import GeolocationManager


@pytest.fixture
def geolocation_provider():
    return MagicMock(spec=GeolocationProvider)


@pytest.fixture
def geolocated_place():
    return GeolocatedPlace(
        place_id="place_id",
        display_name="display_name",
        lat=39.5082456,
        lon=-0.3612918,
    )


def test_get_reverse_geolocation_calls_provider(mocker, geolocation_provider, geolocated_place):
    geolocation_provider.get_reverse_geolocation.return_value = geolocated_place

    geolocation_manager = GeolocationManager(geolocation_provider)
    result = geolocation_manager.get_reverse_geolocation(39.5082456, -0.3612918)

    assert result == geolocated_place
    geolocation_provider.get_reverse_geolocation.assert_called_once_with(39.5082456, -0.3612918)


def test_get_matching_places_calls_provider(mocker, geolocation_provider, geolocated_place):
    geolocation_provider.get_matching_places.return_value = [geolocated_place]

    geolocation_manager = GeolocationManager(geolocation_provider)
    result = geolocation_manager.get_matching_places("query_text")

    assert result == [geolocated_place]
    geolocation_provider.get_matching_places.assert_called_once_with("query_text")
