from datetime import datetime, timedelta

import pytest

from app.models import GreedyPlayersFilter, MatchFilter
from app.services.common import get_weekly_dates


class TestGetWeeklyDatesMatchFilter:
    def test_get_weekly_dates_with_valid_match_filter(self) -> None:
        match_filter = MatchFilter(days="0123")
        expected_dates = [
            (datetime.now() + timedelta(days=0)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=2)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d"),
        ]
        assert get_weekly_dates(match_filter) == expected_dates

    def test_get_weekly_dates_with_empty_days_match_filter(self) -> None:
        match_filter = MatchFilter(days="")
        expected_dates: list = []
        assert get_weekly_dates(match_filter) == expected_dates

    def test_get_weekly_dates_with_invalid_days_match_filter(self) -> None:
        with pytest.raises(ValueError):
            MatchFilter(days="01234567")


class TestGetWeeklyDatesGreedyPlayersFilter:
    def test_get_weekly_dates_with_valid_greedy_players_filter(self) -> None:
        greedy_players_filter = GreedyPlayersFilter(days="456")
        expected_dates = [
            (datetime.now() + timedelta(days=4)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=5)).strftime("%Y-%m-%d"),
            (datetime.now() + timedelta(days=6)).strftime("%Y-%m-%d"),
        ]
        assert get_weekly_dates(greedy_players_filter) == expected_dates

    def test_get_weekly_dates_with_empty_days_greedy_players_filter(self) -> None:
        greedy_players_filter = GreedyPlayersFilter(days="")
        expected_dates: list = []
        assert get_weekly_dates(greedy_players_filter) == expected_dates

    def test_get_weekly_dates_with_invalid_days_greedy_players_filter(self) -> None:
        with pytest.raises(ValueError):
            GreedyPlayersFilter(days="01234567")
