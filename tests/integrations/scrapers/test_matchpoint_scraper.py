from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time
from pytest import fixture, mark

from app.integrations.scrapers import MatchpointScraper
from app.models import MatchFilter, SiteInfo, SiteType


@freeze_time("2024-06-11")
@mark.usefixtures("patch_cache")
class TestMatchpointScrapCourtData:
    BOOKING_HTML = """
    <div>
        <form name="aspnetForm" method="post" action="Grid.aspx" id="aspnetForm">
            <div>
                <input type="hidden" name="__VIEWSTATE" id="__VIEWSTATE" value="value1" />
            </div>
            <script type="text/javascript"></script>
            <script type="text/javascript">
            //<![CDATA[
            hl90njda2b89k='c00lk3y==';var __cultureInfo = '{"name":"es-ES"}';//]]>
            </script>
    </div>
    """
    SPORT_LIST_RESPONSE = {"d": [{"Id": 5, "Nombre": "TeniS"}, {"Id": 4, "Nombre": "PádEl"}]}
    COURT_LIST_RESPONSE = {
        "d": {
            "Columnas": [
                {
                    "Id": 1,
                    "TextoPrincipal": "Court 1",
                    "HorariosFijos": [{"StrHoraInicio": "10:00"}, {"StrHoraInicio": "12:00"}],
                },
                {
                    "Id": 2,
                    "TextoPrincipal": "Court 2",
                    "HorariosFijos": [{"StrHoraInicio": "10:30"}, {"StrHoraInicio": "13:30"}],
                },
            ]
        }
    }

    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT),
            SiteInfo(url="test.com", name="Test", type=SiteType.MATCHPOINT),
        ]

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.get")
    def test_get_api_key(self, mock_requests_get):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        scraper = MatchpointScraper()

        mock_response = Mock()
        mock_response.text = self.BOOKING_HTML

        mock_requests_get.return_value = mock_response

        expected_api_key = "c00lk3y=="

        api_key = scraper._get_api_key(site)

        assert api_key == expected_api_key
        mock_requests_get.assert_called_once_with("https://example.com/Booking/Grid.aspx")

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.get")
    def test_get_api_key_value_error(self, mock_requests_get):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        scraper = MatchpointScraper()

        mock_response = Mock()
        mock_response.text = "Invent"
        mock_requests_get.return_value = mock_response

        with pytest.raises(ValueError) as exc_info:
            scraper._get_api_key(site)
            assert str(exc_info.value) == "hl90njda2b89k key not found"

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    def test_get_sport_ids(self, mock_requests_post):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        scraper = MatchpointScraper()

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        expected_sport_ids = [5, 4]
        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        sport_ids = scraper._get_sport_ids(site, match_filter, "c00lk3y==")

        assert sport_ids == expected_sport_ids
        mock_requests_post.assert_called_once_with(
            "https://example.com/booking/srvc.aspx/ObtenerCuadros", json={"key": "c00lk3y=="}
        )

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    def test_get_sport_ids_filter_by_sport(self, mock_requests_post):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        scraper = MatchpointScraper()

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        padel_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="padel")
        tenis_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="tenis")

        tenis_sport_ids = scraper._get_sport_ids(site, tenis_filter, "c00lk3y==")
        padel_sport_ids = scraper._get_sport_ids(site, padel_filter, "c00lk3y==")

        assert tenis_sport_ids == [5]
        assert padel_sport_ids == [4]

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    def test_get_sport_ids_filter_by_sport_not_found(self, mock_requests_post):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        scraper = MatchpointScraper()

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="pickleball or something worse")

        sport_ids = scraper._get_sport_ids(site, match_filter, "c00lk3y==")
        assert sport_ids == []

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_court_data(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):
        scraper = MatchpointScraper()

        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        result = scraper.get_court_data(match_filter, sites[0])
        assert len(result) == 3
        assert result[0].time == "10:00"
        assert result[1].time == "12:00"
        assert result[2].time == "10:30"

    @freeze_time("2024-06-11 11:00")
    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_court_data_past_date(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):
        scraper = MatchpointScraper()

        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        result = scraper.get_court_data(match_filter, sites[0])
        assert len(result) == 1
        assert result[0].time == "12:00"

    @patch("app.integrations.scrapers.matchpoint_scraper.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_court_data_filter_date(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):
        scraper = MatchpointScraper()

        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        match_filter = MatchFilter(days="0", time_min="10:29", time_max="13:29")

        result = scraper.get_court_data(match_filter, sites[0])
        assert len(result) == 2
        assert result[0].time == "12:00"
        assert result[1].time == "10:30"
