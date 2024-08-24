from unittest.mock import Mock, patch

from freezegun import freeze_time
from pytest import fixture, mark

from app.integrations.scrapers import WebsdepadelScraper
from app.models import MatchFilter, SiteInfo, SiteType


@freeze_time("2024-06-11")
@mark.usefixtures("patch_cache")
@patch("app.integrations.scrapers.websdepadel_scraper.requests.get")
class TestWebsDePadelScrapCourtData:
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
                    <a href="http://example.com/match3">13:00</a>
                </li>
                <li class="partida">
                    <a href="http://example.com/match5">14:00</a>
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

    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="test.com", name="Test", type=SiteType.WEBSDEPADEL),
        ]

    def test_get_court_data(self, mock_requests_get, example_site):
        """Returns all matches from the HTML content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(match_filter, example_site)
        matches = result[0].matches

        assert len(matches) == 4
        assert matches[0].sport == "Padel"
        assert matches[0].court == "Court 1"
        assert matches[0].time == "10:00"
        assert matches[0].url == "http://example.com/match1"
        assert matches[0].is_available is True

        assert matches[1].sport == "Padel"
        assert matches[1].court == "Court 1"
        assert matches[1].time == "12:00"
        assert matches[1].url == "http://example.com/match2"
        assert matches[1].is_available is False

        assert matches[2].sport == "Padel"
        assert matches[2].court == "Court 2"
        assert matches[2].time == "13:00"
        assert matches[2].url == "http://example.com/match3"
        assert matches[2].is_available is True

        assert matches[3].sport == "Tenis"
        assert matches[3].court == "Court 3"
        assert matches[3].time == "10:00"
        assert matches[3].url == "http://example.com/match4"
        assert matches[3].is_available is True

    @freeze_time("2024-06-11 12:00")
    def test_get_court_data_filters_past_date(self, mock_requests_get, example_site):
        """Returns only matches that are not in the past."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(match_filter, example_site)
        matches = result[0].matches

        assert len(matches) == 2

        assert matches[0].sport == "Padel"
        assert matches[0].court == "Court 1"
        assert matches[0].time == "12:00"

        assert matches[1].sport == "Padel"
        assert matches[1].court == "Court 2"
        assert matches[1].time == "13:00"

    def test_get_court_hour_filter(self, mock_requests_get, example_site):
        """Returns only matches that are not in the past."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="13:30", time_max="14:30")
        result = WebsdepadelScraper().get_court_data(match_filter, example_site)
        matches = result[0].matches

        assert len(matches) == 1

        assert matches[0].sport == "Padel"
        assert matches[0].court == "Court 2"
        assert matches[0].time == "14:00"

    def test_get_court_data_filter_by_sport(self, mock_requests_get, example_site):
        """Returns only matches that match the sport filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by sport "tenis"
        filter_tenis = MatchFilter(sport="tenis", is_available=None, days="0", time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(filter_tenis, example_site)
        matches = result[0].matches
        assert len(matches) == 1
        assert matches[0].sport == "Tenis"

    def test_get_court_data_filter_by_availability(self, mock_requests_get, example_site):
        """Returns only matches that match the availability filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by availability False
        filter_not_available = MatchFilter(is_available=False, days="0", time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(filter_not_available, example_site)
        matches = result[0].matches
        assert len(matches) == 1
        assert matches[0].is_available is False

        # Filter by availability True
        filter_available = MatchFilter(is_available=True, days="0", time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(filter_available, example_site)
        matches = result[0].matches
        assert len(matches) == 3
        assert all(match.is_available is True for match in matches)

    def test_get_court_data_filter_by_days(self, mock_requests_get, example_site):
        """Returns only matches that match the days filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        filter_days_1 = MatchFilter(days="01", sport="Tenis", is_available=None, time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(filter_days_1, example_site)
        assert len(result) == 2
        assert result[0].date == "2024-06-11"
        assert result[1].date == "2024-06-12"

        filter_days_2 = MatchFilter(days="456", sport="Tenis", is_available=None, time_min="10:00", time_max="13:00")
        result = WebsdepadelScraper().get_court_data(filter_days_2, example_site)
        assert len(result) == 3
        assert result[0].date == "2024-06-15"
        assert result[1].date == "2024-06-16"
        assert result[2].date == "2024-06-17"
