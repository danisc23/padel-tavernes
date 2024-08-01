from unittest.mock import patch

from pytest import fixture

from app.integrations.scrapers import PlaytomicScrapper, WebsdepadelScrapper
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteType
from app.services.availability import get_court_data


class TestGetCourtData:
    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="example2.com", name="Example2", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="test.com", name="Test", type=SiteType.PLAYTOMIC),
        ]

    @patch.object(PlaytomicScrapper, "get_court_data", return_value=[])
    @patch.object(WebsdepadelScrapper, "get_court_data", return_value=[])
    def test_get_court_data_calls(self, mock_scrap_websdepadel_court_data, mock_scrap_playtomic_court_data, sites):
        get_court_data(MatchFilter(days="0", time_min="10:00", time_max="13:00"), sites)
        assert mock_scrap_websdepadel_court_data.call_count == 2
        assert mock_scrap_playtomic_court_data.call_count == 1

    @patch.object(WebsdepadelScrapper, "get_court_data")
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
        response = get_court_data(MatchFilter(days="0", time_min="10:00", time_max="13:00"), [sites[0]])

        assert len(response) == 4
        assert response[0].court == "Court 2"
        assert response[1].court == "Court 4"
        assert response[2].court == "Court 1"
        assert response[3].court == "Court 3"
