from unittest.mock import patch

import pytest

from app.models import (
    CourtUsage,
    Match,
    MatchFilter,
    MatchInfo,
    SportUsage,
    UsageResponse,
)
from app.services.usage import get_court_usage


@patch("app.services.usage.get_court_data")
def test_get_court_usage(get_court_data, example_site) -> None:
    get_court_data.return_value = [
        MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-12",
            time="10:00",
            url="_",
            is_available=True,
            site=example_site,
        ),
        MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-12",
            time="11:00",
            url="_",
            is_available=False,
            site=example_site,
        ),
        MatchInfo(
            sport="padel",
            court="Court 2",
            date="2024-06-12",
            time="10:00",
            url="_",
            is_available=False,
            site=example_site,
        ),
        MatchInfo(
            sport="tenis",
            court="Court 3",
            date="2024-06-12",
            time="12:00",
            url="_",
            is_available=False,
            site=example_site,
        ),
    ]

    result = get_court_usage(MatchFilter(days="0"), [example_site])

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


def test_get_court_usage_limited_to_1_site(example_site) -> None:
    with pytest.raises(ValueError) as exc_info:
        get_court_usage(MatchFilter(days="0"), [example_site, example_site])
    assert str(exc_info.value) == "Please provide only one site by using X-SITE header"


def test_scrap_greedy_players_unsupported_site_type(playtomic_site):
    with pytest.raises(ValueError) as exc_info:
        get_court_usage(MatchFilter(days="0"), [playtomic_site])
    assert (
        str(exc_info.value)
        == "Site type playtomic is not supported for usage data. Currently only websdepadel is supported."
    )
