from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from freezegun import freeze_time

from app.models import MatchFilter, MatchInfo
from app.services.availability import check_filters, scrap_court_data


@freeze_time("2024-06-11")
class TestCheckFilters:
    def test_check_filters_sport_matching(self):
        match_info = MatchInfo(
            sport="padel", court="Court 1", date="2024-06-11", time="10:00", url="http://example.com", is_available=True
        )
        match_filter = MatchFilter(sport="padel", is_available=None, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_sport_not_matching(self):
        match_info = MatchInfo(
            sport="tenis", court="Court 1", date="2024-06-11", time="10:00", url="http://example.com", is_available=True
        )
        match_filter = MatchFilter(sport="padel", is_available=None, days="0123456")
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_availability_matching(self):
        match_info = MatchInfo(
            sport="padel", court="Court 1", date="2024-06-11", time="10:00", url="http://example.com", is_available=True
        )
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_availability_not_matching(self):
        match_info = MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-11",
            time="10:00",
            url="http://example.com",
            is_available=False,
        )
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_date_not_past(self):
        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        match_info = MatchInfo(
            sport="padel", court="Court 1", date=future_date, time="10:00", url="http://example.com", is_available=True
        )
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_date_past(self):
        past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        match_info = MatchInfo(
            sport="padel", court="Court 1", date=past_date, time="10:00", url="http://example.com", is_available=True
        )
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is False


@freeze_time("2024-06-11")
class TestScrapCourtData:
    HTML_CONTENT = """
    <div id="resumen-disponibilidad">
        <li class="deporte">
            <span class="nombre">Padel</span>
            <li class="pista">
                <span class="nombre">Court 1</span>
                <li class="partida">
                    <a href="http://example.com/match1">10:00</a>
                </li>
                <li class="partida partida-reservada">
                    <a href="http://example.com/match2">12:00</a>
                </li>
            </li>
            <li class="pista">
                <span class="nombre">Court 2</span>
                <li class="partida">
                    <a href="http://example.com/match3">14:00</a>
                </li>
            </li>
        </li>
        <li class="deporte">
            <span class="nombre">Tenis</span>
            <li class="pista">
                <span class="nombre">Court 3</span>
                <li class="partida">
                    <a href="http://example.com/match4">10:00</a>
                </li>
            </li>
        </li>
    </div>
    """
    SITE = "fakesite.com"

    @patch("app.services.availability.requests.get")
    def test_scrap_court_data(self, mock_requests_get):
        """Returns all matches from the HTML content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0")
        result = scrap_court_data(match_filter, self.SITE)

        assert len(result) == 4
        assert result[0].sport == "Padel"
        assert result[0].court == "Court 1"
        assert result[0].date == "2024-06-11"
        assert result[0].time == "10:00"
        assert result[0].url == "http://example.com/match1"
        assert result[0].is_available is True

        assert result[1].sport == "Padel"
        assert result[1].court == "Court 1"
        assert result[1].date == "2024-06-11"
        assert result[1].time == "12:00"
        assert result[1].url == "http://example.com/match2"
        assert result[1].is_available is False

        assert result[2].sport == "Padel"
        assert result[2].court == "Court 2"
        assert result[2].date == "2024-06-11"
        assert result[2].time == "14:00"
        assert result[2].url == "http://example.com/match3"
        assert result[2].is_available is True

        assert result[3].sport == "Tenis"
        assert result[3].court == "Court 3"
        assert result[3].date == "2024-06-11"
        assert result[3].time == "10:00"
        assert result[3].url == "http://example.com/match4"
        assert result[3].is_available is True

    @patch("app.services.availability.requests.get")
    @freeze_time("2024-06-11 12:00")
    def test_scrap_court_data_filters_past_date(self, mock_requests_get):
        """Returns only matches that are not in the past."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0")
        result = scrap_court_data(match_filter, self.SITE)

        assert len(result) == 2

        assert result[0].sport == "Padel"
        assert result[0].court == "Court 1"
        assert result[0].date == "2024-06-11"
        assert result[0].time == "12:00"

        assert result[1].sport == "Padel"
        assert result[1].court == "Court 2"
        assert result[1].date == "2024-06-11"
        assert result[1].time == "14:00"

    @patch("app.services.availability.requests.get")
    def test_scrap_court_data_filter_by_sport(self, mock_requests_get):
        """Returns only matches that match the sport filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by sport "tenis"
        filter_tenis = MatchFilter(sport="tenis", is_available=None, days="0")
        result = scrap_court_data(filter_tenis, self.SITE)
        assert len(result) == 1
        assert result[0].sport == "Tenis"

    @patch("app.services.availability.requests.get")
    def test_scrap_court_data_filter_by_availability(self, mock_requests_get):
        """Returns only matches that match the availability filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by availability False
        filter_not_available = MatchFilter(is_available=False, days="0")
        result = scrap_court_data(filter_not_available, self.SITE)
        assert len(result) == 1
        assert result[0].is_available is False

        # Filter by availability True
        filter_available = MatchFilter(is_available=True, days="0")
        result = scrap_court_data(filter_available, self.SITE)
        assert len(result) == 3
        assert all(match.is_available is True for match in result)

    @patch("app.services.availability.requests.get")
    def test_scrap_court_data_filter_by_days(self, mock_requests_get):
        """Returns only matches that match the days filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        filter_days_1 = MatchFilter(days="01", sport="Tenis", is_available=None)
        result = scrap_court_data(filter_days_1, self.SITE)
        assert len(result) == 2
        assert result[0].date == "2024-06-11"
        assert result[1].date == "2024-06-12"

        filter_days_2 = MatchFilter(days="23456", sport="Tenis", is_available=None)
        result = scrap_court_data(filter_days_2, self.SITE)
        assert len(result) == 5
        assert result[0].date == "2024-06-13"
        assert result[1].date == "2024-06-14"
        assert result[2].date == "2024-06-15"
        assert result[3].date == "2024-06-16"
        assert result[4].date == "2024-06-17"
