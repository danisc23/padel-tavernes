from unittest.mock import Mock, patch

from freezegun import freeze_time
from pytest import fixture, mark

from app.integrations.scrapers import PlaytomicScraper
from app.models import MatchFilter


@freeze_time("2024-06-20")
@mark.usefixtures("patch_cache")
@patch("app.integrations.scrapers.scraper_interface.requests.Session.get")
class TestPlaytomicScrapCourtData:
    @fixture
    def match_filter(self) -> MatchFilter:
        return MatchFilter(days="0", time_min="12:00", time_max="15:00")

    def test_get_site_matches(self, mock_requests_get, playtomic_site, match_filter):
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

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()
        assert len(result) == 1

        site = result[0]
        assert site.site == playtomic_site
        assert site.date == "2024-06-20"

        matches = result[0].matches
        assert len(matches) == 3
        assert matches[0].sport == "padel"
        assert matches[0].court == "Padel 1"
        assert matches[0].time == "12:00"
        assert matches[0].url == playtomic_site.url
        assert matches[0].is_available is True

        assert matches[1].sport == "padel"
        assert matches[1].court == "Padel 1"
        assert matches[1].time == "14:00"
        assert matches[1].url == playtomic_site.url
        assert matches[1].is_available is True

        assert matches[2].sport == "padel"
        assert matches[2].court == "Padel 2"
        assert matches[2].time == "16:00"
        assert matches[2].url == playtomic_site.url
        assert matches[2].is_available is True

    @freeze_time("2024-06-11 12:01")
    def test_get_site_matches_filters_past_date(self, mock_requests_get, playtomic_site, match_filter):
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

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()

        matches = result[0].matches

        assert len(result) == 1
        assert len(matches) == 1
        assert matches[0].sport == "padel"
        assert matches[0].court == "Padel 1"
        assert matches[0].time == "16:00"

    def test_get_site_matches_filters_by_duration(self, mock_requests_get, playtomic_site, match_filter):
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

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()

        matches = result[0].matches

        assert len(result) == 1
        assert len(matches) == 1
        assert matches[0].sport == "padel"
        assert matches[0].court == "Padel 1"
        assert matches[0].time == "12:00"

    def test_get_site_matches_filters_next_hour_slots(self, mock_requests_get, playtomic_site, match_filter):
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

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()

        matches = result[0].matches

        assert len(result) == 1
        assert len(matches) == 2
        assert matches[0].time == "12:00"
        assert matches[1].time == "13:30"

    def test_get_site_matches_request_time_to_localtime(self, mock_requests_get, playtomic_site, match_filter):
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

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()

        matches = result[0].matches

        assert len(result) == 1
        assert len(matches) == 1
        assert matches[0].time == "12:00"

    def test_get_site_matches_1_site_matches_per_date(self, mock_requests_get, playtomic_site):
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

        match_filter = MatchFilter(days="01", time_min="12:00", time_max="15:00")

        result = PlaytomicScraper(playtomic_site, match_filter).get_site_matches()
        assert len(result) == 2
        assert result[0].date == "2024-06-20"
        assert result[1].date == "2024-06-21"
