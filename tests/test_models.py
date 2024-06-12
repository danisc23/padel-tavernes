import pytest
from pydantic import ValidationError

from app.models import GreedyPlayerInfo, GreedyPlayersFilter, MatchFilter, MatchInfo


class TestMatchInfo:
    def test_match_info_creation(self) -> None:
        match_info = MatchInfo(
            sport="padel", court="Court 1", date="2024-06-12", time="10:00", url="http://example.com", is_available=True
        )
        assert match_info.sport == "padel"
        assert match_info.court == "Court 1"
        assert match_info.date == "2024-06-12"
        assert match_info.time == "10:00"
        assert match_info.url == "http://example.com"
        assert match_info.is_available is True


class TestMatchFilter:
    def test_match_filter_creation_valid_days(self) -> None:
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert match_filter.sport == "padel"
        assert match_filter.is_available is True
        assert match_filter.days == "0123456"

    def test_match_filter_invalid_days(self) -> None:
        with pytest.raises(ValidationError):
            MatchFilter(sport="padel", is_available=True, days="01234567")

    def test_match_filter_non_unique_days(self) -> None:
        with pytest.raises(ValidationError):
            MatchFilter(sport="padel", is_available=True, days="0012345")


class TestGreedyPlayerInfo:
    def test_greedy_player_info_creation(self) -> None:
        player_info = GreedyPlayerInfo(
            name="Player1", count=5, dates={"2024-06-12", "2024-06-13"}, hours=["10:00", "12:00"]
        )
        assert player_info.name == "Player1"
        assert player_info.count == 5
        assert player_info.dates == {"2024-06-12", "2024-06-13"}
        assert player_info.hours == ["10:00", "12:00"]
        assert player_info.different_dates == 2


class TestGreedyPlayersFilter:
    def test_greedy_players_filter_creation_valid_sport(self) -> None:
        filter = GreedyPlayersFilter(sport="padel", days="0123456")
        assert filter.sport == "padel"
        assert filter.days == "0123456"

    def test_greedy_players_filter_invalid_sport(self) -> None:
        with pytest.raises(ValidationError):
            GreedyPlayersFilter(sport="basketball", days="0123456")

    def test_greedy_players_filter_creation_valid_days(self) -> None:
        filter = GreedyPlayersFilter(sport="padel", days="0123456")
        assert filter.sport == "padel"
        assert filter.days == "0123456"
