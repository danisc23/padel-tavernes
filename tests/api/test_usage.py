from unittest.mock import patch

from app.models import CourtUsage, Match, SportUsage, UsageResponse


@patch("app.api.usage.get_court_usage")
def test_get_court_usage(mock_get_court_usage, client) -> None:
    mock_get_court_usage.return_value = UsageResponse(
        sports=[
            SportUsage(
                name="padel",
                courts=[
                    CourtUsage(
                        name="Court 1",
                        matches=[
                            Match(date="2024-06-12", time="10:00", is_available=True),
                            Match(date="2024-06-12", time="11:00", is_available=False),
                        ],
                    ),
                    CourtUsage(
                        name="Court 2",
                        matches=[
                            Match(date="2024-06-12", time="10:00", is_available=False),
                        ],
                    ),
                ],
            ),
            SportUsage(
                name="tenis",
                courts=[
                    CourtUsage(
                        name="Court 3",
                        matches=[
                            Match(date="2024-06-12", time="12:00", is_available=False),
                        ],
                    ),
                ],
            ),
        ]
    )

    response = client.get("/api/usage/")

    expected = {
        "sports": [
            {
                "name": "padel",
                "total_booked": 2,
                "total_available": 1,
                "total_matches": 3,
                "booked_percentage": 66.67,
                "courts": [
                    {
                        "name": "Court 1",
                        "total_booked": 1,
                        "total_available": 1,
                        "total_matches": 2,
                        "booked_percentage": 50.0,
                    },
                    {
                        "name": "Court 2",
                        "total_booked": 1,
                        "total_available": 0,
                        "total_matches": 1,
                        "booked_percentage": 100.0,
                    },
                ],
            },
            {
                "name": "tenis",
                "total_booked": 1,
                "total_available": 0,
                "total_matches": 1,
                "booked_percentage": 100.0,
                "courts": [
                    {
                        "name": "Court 3",
                        "total_booked": 1,
                        "total_available": 0,
                        "total_matches": 1,
                        "booked_percentage": 100.0,
                    }
                ],
            },
        ],
        "total_booked": 3,
        "total_available": 1,
        "total_matches": 4,
        "booked_percentage": 75.0,
    }

    assert response.json == expected
