import pytest
from pydantic import ValidationError

from app.models import MatchFilter, MatchInfo


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
    def test_match_filter_creation_valid(self) -> None:
        match_filter = MatchFilter(sport="padel", is_available=True, days="012", time_min="10:00", time_max="13:00")
        MatchFilter(sport="padel", is_available=True, days="01", time_min="10:00", time_max="13:00")
        MatchFilter(sport="padel", is_available=True, days="0", time_min="10:00", time_max="13:00")
        assert match_filter.sport == "padel"
        assert match_filter.is_available is True
        assert match_filter.days == "012"
        assert match_filter.time_min == "10:00"
        assert match_filter.time_max == "13:00"

    def test_match_filter_invalid_days_quantity(self) -> None:
        with pytest.raises(ValidationError) as exc_info_more:
            MatchFilter(sport="padel", is_available=True, days="0123", time_min="10:00", time_max="13:00")

        with pytest.raises(ValidationError) as exc_info_empty:
            MatchFilter(sport="padel", is_available=True, days="", time_min="10:00", time_max="13:00")

        assert "days must be a string containing 1 to 3 digits" in str(exc_info_more.value)
        assert "days must be a string containing 1 to 3 digits" in str(exc_info_empty.value)

    def test_match_filter_non_unique_days(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="001", time_min="10:00", time_max="13:00")
        assert "days must have unique digits" in str(exc_info.value)

    def test_match_filter_invalid_days_number(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="567", time_min="10:00", time_max="13:00")
        assert "days must have digits between 0 and 6" in str(exc_info.value)

    def test_match_filter_invalid_days_must_be_consecutive(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="013", time_min="10:00", time_max="13:00")
        assert "days must be consecutive" in str(exc_info.value)

    def test_match_filter_invalid_time_format(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="012", time_min="10:00:00", time_max="25:00")
        assert "time_min must be a string in the format HH:MM" in str(exc_info.value)
        assert "time_max must be a string in the format HH:MM" in str(exc_info.value)

    def test_match_filter_invalid_time_range_min_greater_than_max(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="012", time_min="10:00", time_max="09:00")
        assert "time_max must be greater than time_min" in str(exc_info.value)

    def test_match_filter_invalid_time_range_exceeds_3_hours(self) -> None:
        with pytest.raises(ValidationError) as exc_info:
            MatchFilter(sport="padel", is_available=True, days="012", time_min="10:00", time_max="14:00")
        assert "The difference between time_min and time_max must not exceed 3 hours" in str(exc_info.value)
