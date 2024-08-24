from unittest.mock import patch

from flask import Response
from freezegun import freeze_time

from app.models import MatchInfo, SiteMatches


@patch("app.api.availability.get_court_data")
def test_get_returns_response(mock_get_court_data, client) -> None:
    mock_get_court_data.return_value = []
    response = client.get("/api/availability/?sport=padel")
    assert isinstance(response, Response)


@freeze_time("2024-06-11 10:00:00")
def test_get_returns_json_response_with_court_data(mocker, client, example_site) -> None:
    """Information returned by the API is the same as the one returned by the scrap_websdepadel_court_data service
    so this is straightforward to test."""

    return_value = [
        SiteMatches(
            site=example_site,
            date="2024-06-11",
            distance_km=0.0,
            matches=[
                MatchInfo(
                    sport="padel",
                    court="Court 1",
                    time="10:00",
                    url="http://example.com/match1",
                    is_available=True,
                ),
                MatchInfo(
                    sport="tenis",
                    court="Court 2",
                    time="12:00",
                    url="http://example.com/match2",
                    is_available=False,
                ),
            ],
        )
    ]
    mocker.patch("app.api.availability.get_court_data", return_value=return_value)

    response = client.get("/api/availability/?sport=padel")
    json_data = response.get_json()
    matches = json_data[0]["matches"]

    assert isinstance(json_data, list)
    assert len(json_data) == 1
    assert json_data[0]["date"] == "2024-06-11"

    assert len(matches) == 2
    assert matches[0]["sport"] == "padel"
    assert matches[0]["court"] == "Court 1"
    assert matches[0]["time"] == "10:00"
    assert matches[0]["url"] == "http://example.com/match1"
    assert matches[0]["is_available"] is True
    assert matches[1]["sport"] == "tenis"
    assert matches[1]["court"] == "Court 2"
    assert matches[1]["time"] == "12:00"
    assert matches[1]["url"] == "http://example.com/match2"
    assert matches[1]["is_available"] is False
