from unittest.mock import patch

from app.integrations.geolocation.location_iq import LocationIQProvider
from app.models import GeolocatedPlace


@patch("app.integrations.geolocation.location_iq.requests.get")
def test_get_reverse_geolocation(mock_get):
    mock_response = {
        "place_id": "12345",
        "display_name": "Sample Place",
        "lat": 39.123456,
        "lon": -0.654321,
    }
    mock_get.return_value.json.return_value = mock_response

    result = LocationIQProvider().get_reverse_geolocation(39.123456, -0.654321)

    assert isinstance(result, GeolocatedPlace)
    assert result.place_id == "12345"
    assert result.display_name == "Sample Place"
    assert result.lat == 39.123456
    assert result.lon == -0.654321


@patch("app.integrations.geolocation.location_iq.requests.get")
def test_get_matching_places(mock_get):
    mock_response = [
        {
            "place_id": "12345",
            "display_name": "Sample Place 1",
            "lat": 39.123456,
            "lon": -0.654321,
        },
        {
            "place_id": "67890",
            "display_name": "Sample Place 2",
            "lat": 39.987654,
            "lon": -0.123456,
        },
    ]
    mock_get.return_value.json.return_value = mock_response

    result = LocationIQProvider().get_matching_places("sample query")

    assert isinstance(result, list)
    assert len(result) == 2

    assert isinstance(result[0], GeolocatedPlace)
    assert result[0].place_id == "12345"
    assert result[0].display_name == "Sample Place 1"
    assert result[0].lat == 39.123456
    assert result[0].lon == -0.654321

    assert isinstance(result[1], GeolocatedPlace)
    assert result[1].place_id == "67890"
    assert result[1].display_name == "Sample Place 2"
    assert result[1].lat == 39.987654
    assert result[1].lon == -0.123456
