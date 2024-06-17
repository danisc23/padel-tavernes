import pytest
from pydantic import ValidationError

from app.models import (
    CourtUsage,
    GreedyPlayerInfo,
    GreedyPlayersFilter,
    Match,
    MatchFilter,
    MatchInfo,
    SportUsage,
    UsageResponse,
)


class TestMatchInfo:
    def test_match_info_creation(self, example_site) -> None:
        match_info = MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-12",
            time="10:00",
            url="http://example.com",
            is_available=True,
            site=example_site,
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


class TestUsageModels:
    match1 = Match(date="2024-06-12", time="10:00", is_available=True)
    match2 = Match(date="2024-06-12", time="11:00", is_available=False)
    match3 = Match(date="2024-06-12", time="12:00", is_available=False)
    match4 = Match(date="2024-06-12", time="13:00", is_available=False)
    match5 = Match(date="2024-06-12", time="10:00", is_available=True)
    match6 = Match(date="2024-06-12", time="11:00", is_available=False)

    court_usage = CourtUsage(name="Padel Court 1", matches=[match1, match2])
    court_usage2 = CourtUsage(name="Padel Court 2", matches=[match3, match4])
    court_usage3 = CourtUsage(name="Tennis Court 1", matches=[match1, match2])

    sport_usage = SportUsage(name="Padel", courts=[court_usage, court_usage2])
    sport_usage2 = SportUsage(name="Tennis", courts=[court_usage3])

    usage_response = UsageResponse(sports=[sport_usage, sport_usage2])

    def test_match(self) -> None:
        """Nothing to test here honestly."""
        assert self.match1.date == "2024-06-12"
        assert self.match1.time == "10:00"
        assert self.match1.is_available is True

    def test_court_usage(self) -> None:
        """Test that the properties returns correct values by court."""
        assert self.court_usage.name == "Padel Court 1"
        assert self.court_usage.total_booked == 1
        assert self.court_usage.total_available == 1
        assert self.court_usage.total_matches == 2
        assert self.court_usage.booked_percentage == 50.0

    def test_sport_usage(self) -> None:
        """Test that the properties returns correct values by sport."""
        assert self.sport_usage.name == "Padel"
        assert self.sport_usage.total_booked == 3
        assert self.sport_usage.total_available == 1
        assert self.sport_usage.total_matches == 4
        assert self.sport_usage.booked_percentage == 75.0

    def test_usage_response(self) -> None:
        """
        Test that the properties returns correct values for everything.
        Test that the booked_percentage is rounded to 2 decimal places.
        """
        assert self.usage_response.total_booked == 4
        assert self.usage_response.total_available == 2
        assert self.usage_response.total_matches == 6
        assert self.usage_response.booked_percentage == 66.67

    def test_empty_usage_response(self) -> None:
        """Test that the properties returns correct values for an empty response."""
        response = UsageResponse(sports=[])
        assert response.total_booked == 0
        assert response.total_available == 0
        assert response.total_matches == 0
        assert response.booked_percentage == 100

    def test_model_dump_with_computed_properties(self) -> None:
        """Test that the model_dump method returns the computed properties recursively"""
        dumped = self.usage_response.model_dump()
        assert "total_booked" in dumped
        assert "total_available" in dumped
        assert "total_matches" in dumped
        assert "booked_percentage" in dumped
        assert "sports" in dumped

        sport = dumped["sports"][0]
        assert "total_booked" in sport
        assert "total_available" in sport
        assert "total_matches" in sport
        assert "booked_percentage" in sport
        assert "courts" in sport
        assert "name" in sport

        court = sport["courts"][0]
        assert "total_booked" in court
        assert "total_available" in court
        assert "total_matches" in court
        assert "booked_percentage" in court
        assert "matches" in court
        assert "name" in court

        match = court["matches"][0]
        assert "date" in match
        assert "time" in match
        assert "is_available" in match
