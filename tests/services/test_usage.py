from unittest.mock import patch

from app.models import (
    CourtUsage,
    Match,
    MatchFilter,
    MatchInfo,
    SportUsage,
    UsageResponse,
)
from app.services.usage import get_court_usage


@patch("app.services.usage.scrap_court_data")
def test_get_court_usage(mock_scrap_court_data) -> None:
    mock_scrap_court_data.return_value = [
        MatchInfo(sport="padel", court="Court 1", date="2024-06-12", time="10:00", url="_", is_available=True),
        MatchInfo(sport="padel", court="Court 1", date="2024-06-12", time="11:00", url="_", is_available=False),
        MatchInfo(sport="padel", court="Court 2", date="2024-06-12", time="10:00", url="_", is_available=False),
        MatchInfo(
            sport="tenis",
            court="Court 3",
            date="2024-06-12",
            time="12:00",
            url="_",
            is_available=False,
        ),
    ]

    result = get_court_usage(MatchFilter(days="0"), "site.com")

    expected = UsageResponse(
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

    assert result == expected
