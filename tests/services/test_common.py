from datetime import datetime, timedelta

import pytest
from freezegun import freeze_time

from app.models import MatchFilter, MatchInfo
from app.services.common import check_filters, get_weekly_dates


class TestGetWeeklyDatesMatchFilter:
    def test_get_weekly_dates_with_valid_match_filter(self) -> None:
        match_filter = MatchFilter(days="012", time_min="10:00", time_max="13:00")
        expected_dates = [
            (datetime.now() + timedelta(days=0)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
        ]
        assert get_weekly_dates(match_filter) == expected_dates


@freeze_time("2024-06-11")
class TestCheckFilters:
    @pytest.fixture
    def match_info(self, example_site) -> MatchInfo:
        return MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-11",
            time="10:00",
            url="http://example.com/match1",
            is_available=True,
            site=example_site,
        )

    @pytest.fixture
    def match_filter(self) -> MatchFilter:
        return MatchFilter(sport="padel", is_available=True, days="012", time_min="10:00", time_max="13:00")

    def test_check_filters_sport_matching(self, match_info, match_filter):
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_sport_not_matching(self, match_info, match_filter):
        match_info.sport = "tenis"
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_availability_matching(self, match_info, match_filter):
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_availability_not_matching(self, match_info, match_filter):
        match_info.is_available = False
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_date_not_past(self, match_info, match_filter):
        match_info.date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_date_past(self, match_info, match_filter):
        match_info.date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        assert check_filters(match_info, match_filter) is False
