from datetime import datetime, timedelta
from unittest.mock import Mock, patch

from freezegun import freeze_time
from pytest import fixture

from app.models import MatchFilter, MatchInfo, SiteInfo, SiteType
from app.services.availability import (
    check_filters,
    get_court_data,
    scrap_playtomic_court_data,
    scrap_websdepadel_court_data,
)


@freeze_time("2024-06-11")
class TestCheckFilters:
    @fixture
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

    def test_check_filters_sport_matching(self, match_info):
        match_filter = MatchFilter(sport="padel", is_available=None, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_sport_not_matching(self, match_info):
        match_info.sport = "tenis"
        match_filter = MatchFilter(sport="padel", is_available=None, days="0123456")
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_availability_matching(self, match_info):
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_availability_not_matching(self, match_info):
        match_info.is_available = False
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is False

    def test_check_filters_date_not_past(self, match_info):
        match_info.date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is True

    def test_check_filters_date_past(self, match_info):
        match_info.date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
        match_filter = MatchFilter(sport="padel", is_available=True, days="0123456")
        assert check_filters(match_info, match_filter) is False


@freeze_time("2024-06-20")
class TestScrapPlaytomicCourtData:
    @fixture
    def match_filter(self) -> MatchFilter:
        return MatchFilter(days="0")

    @patch("app.services.availability.requests.get")
    def test_scrap_playtomic_court_data(self, mock_requests_get, playtomic_site, match_filter):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "resource_id": "court1",
                "slots": [
                    {"start_time": "10:00:00", "duration": 90},
                    {"start_time": "12:00:00", "duration": 90},
                ],
            },
            {
                "resource_id": "court2",
                "slots": [
                    {"start_time": "14:00:00", "duration": 90},
                ],
            },
        ]
        mock_requests_get.return_value = mock_response

        result = scrap_playtomic_court_data(match_filter, playtomic_site)

        assert len(result) == 3
        assert result[0].sport == "padel"
        assert result[0].court == "Padel 1"
        assert result[0].date == "2024-06-20"
        assert result[0].time == "12:00"
        assert result[0].url == playtomic_site.url
        assert result[0].is_available is True

        assert result[1].sport == "padel"
        assert result[1].court == "Padel 1"
        assert result[1].date == "2024-06-20"
        assert result[1].time == "14:00"
        assert result[1].url == playtomic_site.url
        assert result[1].is_available is True

        assert result[2].sport == "padel"
        assert result[2].court == "Padel 2"
        assert result[2].date == "2024-06-20"
        assert result[2].time == "16:00"
        assert result[2].url == playtomic_site.url
        assert result[2].is_available is True

    @patch("app.services.availability.requests.get")
    @freeze_time("2024-06-11 12:01")
    def test_scrap_playtomic_court_data_filters_past_date(self, mock_requests_get, playtomic_site, match_filter):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "resource_id": "court1",
                "slots": [
                    {"start_time": "10:00:00", "duration": 90},
                    {"start_time": "12:00:00", "duration": 90},
                ],
            },
            {
                "resource_id": "court2",
                "slots": [
                    {"start_time": "14:00:00", "duration": 90},
                ],
            },
        ]
        mock_requests_get.return_value = mock_response

        result = scrap_playtomic_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].sport == "padel"
        assert result[0].court == "Padel 2"
        assert result[0].date == "2024-06-11"
        assert result[0].time == "16:00"

    @patch("app.services.availability.requests.get")
    def test_scrap_playtomic_court_data_filters_by_duration(self, mock_requests_get, playtomic_site, match_filter):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "resource_id": "court1",
                "slots": [
                    {"start_time": "10:00:00", "duration": 60},
                    {"start_time": "10:00:00", "duration": 90},
                    {"start_time": "10:00:00", "duration": 120},
                ],
            },
        ]
        mock_requests_get.return_value = mock_response

        result = scrap_playtomic_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].sport == "padel"
        assert result[0].court == "Padel 1"
        assert result[0].date == "2024-06-20"
        assert result[0].time == "12:00"

    @patch("app.services.availability.requests.get")
    def test_scrap_playtomic_court_data_filters_next_hour_slots(self, mock_requests_get, playtomic_site, match_filter):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "resource_id": "court1",
                "slots": [
                    {"start_time": "10:00:00", "duration": 90},
                    {"start_time": "10:30:00", "duration": 90},
                    {"start_time": "11:00:00", "duration": 90},
                    {"start_time": "11:30:00", "duration": 90},
                ],
            },
        ]
        mock_requests_get.return_value = mock_response

        result = scrap_playtomic_court_data(match_filter, playtomic_site)

        assert len(result) == 2
        assert result[0].time == "12:00"
        assert result[1].time == "13:30"

    @patch("app.services.availability.requests.get")
    def test_scrap_playtomic_court_data_request_time_to_localtime(
        self, mock_requests_get, playtomic_site, match_filter
    ):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {
                "resource_id": "court1",
                "slots": [
                    {"start_time": "10:00:00", "duration": 90},
                ],
            },
        ]
        mock_requests_get.return_value = mock_response

        result = scrap_playtomic_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].time == "12:00"


@freeze_time("2024-06-11")
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

    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="test.com", name="Test", type=SiteType.WEBSDEPADEL),
        ]

    @patch("app.services.availability.requests.get")
    def test_scrap_websdepadel_court_data(self, mock_requests_get, example_site):
        """Returns all matches from the HTML content."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0")
        result = scrap_websdepadel_court_data(match_filter, example_site)

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
    def test_scrap_websdepadel_court_data_filters_past_date(self, mock_requests_get, example_site):
        """Returns only matches that are not in the past."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        match_filter = MatchFilter(days="0")
        result = scrap_websdepadel_court_data(match_filter, example_site)

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
    def test_scrap_websdepadel_court_data_filter_by_sport(self, mock_requests_get, example_site):
        """Returns only matches that match the sport filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by sport "tenis"
        filter_tenis = MatchFilter(sport="tenis", is_available=None, days="0")
        result = scrap_websdepadel_court_data(filter_tenis, example_site)
        assert len(result) == 1
        assert result[0].sport == "Tenis"

    @patch("app.services.availability.requests.get")
    def test_scrap_websdepadel_court_data_filter_by_availability(self, mock_requests_get, example_site):
        """Returns only matches that match the availability filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        # Filter by availability False
        filter_not_available = MatchFilter(is_available=False, days="0")
        result = scrap_websdepadel_court_data(filter_not_available, example_site)
        assert len(result) == 1
        assert result[0].is_available is False

        # Filter by availability True
        filter_available = MatchFilter(is_available=True, days="0")
        result = scrap_websdepadel_court_data(filter_available, example_site)
        assert len(result) == 3
        assert all(match.is_available is True for match in result)

    @patch("app.services.availability.requests.get")
    def test_scrap_websdepadel_court_data_filter_by_days(self, mock_requests_get, example_site):
        """Returns only matches that match the days filter."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        filter_days_1 = MatchFilter(days="01", sport="Tenis", is_available=None)
        result = scrap_websdepadel_court_data(filter_days_1, example_site)
        assert len(result) == 2
        assert result[0].date == "2024-06-11"
        assert result[1].date == "2024-06-12"

        filter_days_2 = MatchFilter(days="23456", sport="Tenis", is_available=None)
        result = scrap_websdepadel_court_data(filter_days_2, example_site)
        assert len(result) == 5
        assert result[0].date == "2024-06-13"
        assert result[1].date == "2024-06-14"
        assert result[2].date == "2024-06-15"
        assert result[3].date == "2024-06-16"
        assert result[4].date == "2024-06-17"


class TestGetCourtData:
    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="example2.com", name="Example2", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="test.com", name="Test", type=SiteType.PLAYTOMIC),
        ]

    @patch("app.services.availability.scrap_playtomic_court_data")
    @patch("app.services.availability.scrap_websdepadel_court_data")
    def test_get_court_data_calls(self, mock_scrap_websdepadel_court_data, mock_scrap_playtomic_court_data, sites):
        get_court_data(MatchFilter(days="0"), sites)
        assert mock_scrap_websdepadel_court_data.call_count == 2
        assert mock_scrap_playtomic_court_data.call_count == 1

    @patch("app.services.availability.scrap_websdepadel_court_data")
    def test_get_court_data_sorts(self, mock_scrap_websdepadel_court_data, sites):
        """Sorts the matches by date and time."""
        match1 = MatchInfo(
            sport="padel",
            court="Court 1",
            date="2024-06-12",
            time="10:00",
            url="http://example.com/match1",
            is_available=True,
            site=sites[0],
        )
        match2 = MatchInfo(
            sport="padel",
            court="Court 2",
            date="2024-06-11",
            time="12:00",
            url="http://example.com/match2",
            is_available=True,
            site=sites[0],
        )
        match3 = MatchInfo(
            sport="padel",
            court="Court 3",
            date="2024-06-12",
            time="11:00",
            url="http://example.com/match3",
            is_available=True,
            site=sites[0],
        )
        match4 = MatchInfo(
            sport="padel",
            court="Court 4",
            date="2024-06-11",
            time="13:00",
            url="http://example.com/match4",
            is_available=True,
            site=sites[0],
        )

        mock_scrap_websdepadel_court_data.return_value = [match1, match2, match3, match4]
        response = get_court_data(MatchFilter(days="0"), [sites[0]])

        assert len(response) == 4
        assert response[0].court == "Court 2"
        assert response[1].court == "Court 4"
        assert response[2].court == "Court 1"
        assert response[3].court == "Court 3"
