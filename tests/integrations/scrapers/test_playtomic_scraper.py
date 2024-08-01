from unittest.mock import Mock, patch

from freezegun import freeze_time
from pytest import fixture, mark

from app.integrations.scrapers import PlaytomicScrapper
from app.models import MatchFilter


@fixture(scope="module")
def patch_cache():
    with (
        patch("app.integrations.scrapers.scraper_interface.cache.get") as mock_cache_get,
        patch("app.integrations.scrapers.scraper_interface.cache.set") as mock_cache_set,
    ):
        mock_cache_get.return_value = None
        yield mock_cache_get, mock_cache_set


@freeze_time("2024-06-20")
@mark.usefixtures("patch_cache")
@patch("app.integrations.scrapers.playtomic_scraper.requests.get")
class TestScrapPlaytomicCourtData:
    @fixture
    def match_filter(self) -> MatchFilter:
        return MatchFilter(days="0", time_min="12:00", time_max="15:00")

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

        result = PlaytomicScrapper().get_court_data(match_filter, playtomic_site)

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

        result = PlaytomicScrapper().get_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].sport == "padel"
        assert result[0].court == "Padel 2"
        assert result[0].date == "2024-06-11"
        assert result[0].time == "16:00"

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

        result = PlaytomicScrapper().get_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].sport == "padel"
        assert result[0].court == "Padel 1"
        assert result[0].date == "2024-06-20"
        assert result[0].time == "12:00"

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

        result = PlaytomicScrapper().get_court_data(match_filter, playtomic_site)

        assert len(result) == 2
        assert result[0].time == "12:00"
        assert result[1].time == "13:30"

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

        result = PlaytomicScrapper().get_court_data(match_filter, playtomic_site)

        assert len(result) == 1
        assert result[0].time == "12:00"
