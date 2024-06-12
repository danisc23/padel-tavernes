from unittest.mock import patch

from flask import Response


@patch("app.api.availability.scrap_court_data")
def test_get_returns_response(mock_scrap_court_data, client) -> None:
    mock_scrap_court_data.return_value = []
    response = client.get("/api/padelsuyo.es/availability/?sport=padel")
    assert isinstance(response, Response)


@patch("app.api.availability.scrap_court_data")
def test_get_returns_json_response_with_court_data(mock_scrap_court_data, client) -> None:
    """Information returned by the API is the same as the one returned by the scrap_court_data service
    so this is straightforward to test."""
    mock_scrap_court_data.return_value = [
        {
            "sport": "padel",
            "court": "Court 1",
            "date": "2024-06-11",
            "time": "10:00",
            "url": "http://example.com",
            "is_available": True,
        },
        {
            "sport": "tenis",
            "court": "Court 2",
            "date": "2024-06-12",
            "time": "12:00",
            "url": "http://example.com",
            "is_available": False,
        },
    ]

    response = client.get("/api/padelsuyo.es/availability/?sport=padel")
    json_data = response.get_json()

    assert isinstance(json_data, list)
    assert len(json_data) == 2
    assert json_data[0]["sport"] == "padel"
    assert json_data[0]["court"] == "Court 1"
    assert json_data[0]["date"] == "2024-06-11"
    assert json_data[0]["time"] == "10:00"
    assert json_data[0]["url"] == "http://example.com"
    assert json_data[0]["is_available"] is True
    assert json_data[1]["sport"] == "tenis"
    assert json_data[1]["court"] == "Court 2"
    assert json_data[1]["date"] == "2024-06-12"
    assert json_data[1]["time"] == "12:00"
    assert json_data[1]["url"] == "http://example.com"
    assert json_data[1]["is_available"] is False
