from unittest.mock import Mock, patch

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

    @patch.object(MatchpointScraper, "_get_sport_ids", return_value=[4, 5])
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.get")
    def test_get_api_key(self, mock_requests_get, _):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        mock_response = Mock()
        mock_response.text = self.BOOKING_HTML
        mock_requests_get.return_value = mock_response

        expected_api_key = "c00lk3y=="

        scraper = MatchpointScraper(site, filter)

        assert scraper.key == expected_api_key
        mock_requests_get.assert_called_once_with("https://example.com/Booking/Grid.aspx")

    @patch.object(MatchpointScraper, "_get_sport_ids", return_value=[4, 5])
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.get")
    def test_get_api_key_value_error(self, mock_requests_get, _mock_requests_post):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        mock_response = Mock()
        mock_response.text = "Invent"
        mock_requests_get.return_value = mock_response

        scraper = MatchpointScraper(site, filter)
        assert scraper.key == ""

    @patch.object(MatchpointScraper, "_get_api_key", return_value="c00lk3y==")
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    def test_get_sport_ids(self, mock_requests_post, _):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE
        mock_requests_post.return_value = mock_response

        expected_sport_ids = [5, 4]

        scraper = MatchpointScraper(site, filter)

        assert scraper.sport_ids == expected_sport_ids
        mock_requests_post.assert_called_once_with(
            "https://example.com/booking/srvc.aspx/ObtenerCuadros", json={"key": "c00lk3y=="}
        )

    @patch.object(MatchpointScraper, "_get_api_key", return_value="c00lk3y==")
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    def test_get_sport_ids_filter_by_sport(self, mock_requests_post, _):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        padel_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="padel")
        tenis_filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="tenis")
        padel_scraper = MatchpointScraper(site, padel_filter)
        tenis_scraper = MatchpointScraper(site, tenis_filter)

        assert tenis_scraper.sport_ids == [5]
        assert padel_scraper.sport_ids == [4]

    @patch.object(MatchpointScraper, "_get_api_key", return_value="c00lk3y==")
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    def test_get_sport_ids_filter_by_sport_not_found(self, mock_requests_post, _):
        site = SiteInfo(url="example.com", name="Example", type=SiteType.MATCHPOINT)
        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00", sport="pickleball or something worse")

        mock_response = Mock()
        mock_response.json.return_value = self.SPORT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        scraper = MatchpointScraper(site, filter)
        assert scraper.sport_ids == []

    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_site_matches(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):

        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")

        scraper = MatchpointScraper(sites[0], filter)
        result = scraper.get_site_matches()
        matches = result[0].matches

        assert len(result) == 1
        assert len(matches) == 3
        assert matches[0].time == "10:00"
        assert matches[1].time == "12:00"
        assert matches[2].time == "10:30"

    @freeze_time("2024-06-11 11:00")
    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_site_matches_past_date(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):
        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")
        scraper = MatchpointScraper(sites[0], filter)
        result = scraper.get_site_matches()
        matches = result[0].matches
        assert len(result) == 1
        assert len(matches) == 1
        assert matches[0].time == "12:00"

    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_site_matches_filter_date(self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites):
        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        filter = MatchFilter(days="0", time_min="10:29", time_max="13:29")
        scraper = MatchpointScraper(sites[0], filter)
        result = scraper.get_site_matches()
        matches = result[0].matches
        assert len(result) == 1

        assert len(matches) == 2
        assert matches[0].time == "12:00"
        assert matches[1].time == "10:30"

    @patch.object(MatchpointScraper, "_get_sport_ids", return_value=[])
    @patch.object(MatchpointScraper, "_get_api_key", return_value="c00lk3y==")
    def test_get_site_matches_returns_empty_on_no_sport_ids(self, _mock_get_api_key, _mock_get_sport_ids, sites):
        filter = MatchFilter(days="0", time_min="10:00", time_max="13:00")
        scraper = MatchpointScraper(sites[0], filter)
        result = scraper.get_site_matches()

        assert result == []

    @patch("app.integrations.scrapers.scraper_interface.requests.Session.post")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_sport_ids")
    @patch("app.integrations.scrapers.matchpoint_scraper.MatchpointScraper._get_api_key")
    def test_get_site_matches_1_site_matches_per_date(
        self, mock_get_api_key, mock_get_sport_ids, mock_requests_post, sites
    ):
        mock_get_api_key.return_value = "c00lk3y=="
        mock_get_sport_ids.return_value = [4]

        mock_response = Mock()
        mock_response.json.return_value = self.COURT_LIST_RESPONSE

        mock_requests_post.return_value = mock_response

        filter = MatchFilter(days="01", time_min="10:00", time_max="13:00")
        scraper = MatchpointScraper(sites[0], filter)
        result = scraper.get_site_matches()

        assert len(result) == 2
        assert result[0].date == "2024-06-11"
        assert result[1].date == "2024-06-12"
