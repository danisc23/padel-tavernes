from unittest.mock import patch

from flask import Response

from app.models import GeolocatedPlace


@patch("app.api.geolocation.GeolocationManager.get_reverse_geolocation")
def test_get_reverse_geolocation_returns_response(mock_get_reverse_geolocation, client) -> None:
    mock_get_reverse_geolocation.return_value = GeolocatedPlace(
        place_id="12345",
        display_name="Sample Place",
        lat=39.123456,
        lon=-0.654321,
    )

    response = client.get("/api/geolocation/reverse-geolocation/?latitude=39.123456&longitude=-0.654321")

    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = response.get_json()
    assert json_data["place_id"] == "12345"
    assert json_data["display_name"] == "Sample Place"
    assert json_data["lat"] == 39.123456
    assert json_data["lon"] == -0.654321


@patch("app.api.geolocation.GeolocationManager.get_matching_places")
def test_get_matching_places_returns_response(mock_get_matching_places, client) -> None:
    mock_get_matching_places.return_value = [
        GeolocatedPlace(
            place_id="12345",
            display_name="Sample Place 1",
            lat=39.123456,
            lon=-0.654321,
        ),
        GeolocatedPlace(
            place_id="67890",
            display_name="Sample Place 2",
            lat=39.987654,
            lon=-0.123456,
        ),
    ]

    response = client.get("/api/geolocation/matching-places/?query=sample")

    assert isinstance(response, Response)
    assert response.status_code == 200

    json_data = response.get_json()
    assert isinstance(json_data, list)
    assert len(json_data) == 2

    assert json_data[0]["place_id"] == "12345"
    assert json_data[0]["display_name"] == "Sample Place 1"
    assert json_data[0]["lat"] == 39.123456
    assert json_data[0]["lon"] == -0.654321

    assert json_data[1]["place_id"] == "67890"
    assert json_data[1]["display_name"] == "Sample Place 2"
    assert json_data[1]["lat"] == 39.987654
    assert json_data[1]["lon"] == -0.123456


@patch("app.api.geolocation.GeolocationManager.get_reverse_geolocation")
def test_get_reverse_geolocation_handles_error(mock_get_reverse_geolocation, client) -> None:
    mock_get_reverse_geolocation.side_effect = Exception("An error occurred")

    response = client.get("/api/geolocation/reverse-geolocation/?latitude=39.123456&longitude=-0.654321")

    assert response.status_code == 500
    assert "An error occurred" in response.get_data(as_text=True)


@patch("app.api.geolocation.GeolocationManager.get_matching_places")
def test_get_matching_places_handles_error(mock_get_matching_places, client) -> None:
    mock_get_matching_places.side_effect = Exception("An error occurred")

    response = client.get("/api/geolocation/matching-places/?query=sample")

    assert response.status_code == 500
    assert "An error occurred" in response.get_data(as_text=True)
