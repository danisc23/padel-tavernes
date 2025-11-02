from unittest.mock import patch

from pytest import fixture

from app.integrations.scrapers import WebsdepadelScraper
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteMatches, SiteType
from app.services.availability import get_court_data


class TestGetCourtData:
    @fixture
    def sites(self):
        return [
            SiteInfo(url="example.com", name="Example", type=SiteType.WEBSDEPADEL),
            SiteInfo(url="example2.com", name="Example2", type=SiteType.WEBSDEPADEL),
        ]

    @patch.object(WebsdepadelScraper, "get_site_matches", return_value=[])
    def test_get_court_data_calls(self, mock_scrap_websdepadel_court_data, sites):
        get_court_data(MatchFilter(days="0", time_min="10:00", time_max="13:00"), sites)
        assert mock_scrap_websdepadel_court_data.call_count == 2

    @patch.object(WebsdepadelScraper, "get_site_matches")
    def test_get_court_data_sorts(self, mock_scrap_websdepadel_court_data, sites):
        """Sorts the matches by date and time."""
        match1 = MatchInfo(
            sport="padel",
            court="Court 1",
            time="10:00",
            url="http://example.com/match1",
            is_available=True,
        )
        match2 = MatchInfo(
            sport="padel",
            court="Court 2",
            time="12:00",
            url="http://example.com/match2",
            is_available=True,
        )
        match3 = MatchInfo(
            sport="padel",
            court="Court 3",
            time="11:00",
            url="http://example.com/match3",
            is_available=True,
        )
        match4 = MatchInfo(
            sport="padel",
            court="Court 4",
            time="13:00",
            url="http://example.com/match4",
            is_available=True,
        )
        site_matches = [
            SiteMatches(site=sites[0], date="2024-06-11", distance_km=0.0, matches=[match2, match4]),
            SiteMatches(site=sites[0], date="2024-06-12", distance_km=0.0, matches=[match1, match3]),
        ]

        mock_scrap_websdepadel_court_data.return_value = site_matches
        response = get_court_data(MatchFilter(days="0", time_min="10:00", time_max="13:00"), [sites[0]])
        site_match1, site_match2 = response
        day1_matches, day2_matches = site_match1.matches, site_match2.matches

        assert len(response) == 2
        assert len(day1_matches) == 2
        assert len(day2_matches) == 2
        assert day1_matches[0].court == "Court 2"
        assert day1_matches[1].court == "Court 4"
        assert day2_matches[0].court == "Court 1"
        assert day2_matches[1].court == "Court 3"

    @patch.object(WebsdepadelScraper, "get_site_matches")
    def test_get_court_data_handles_scraper_errors(self, mock_scrap_websdepadel_court_data, sites):
        """Continues processing other sites when one scraper fails."""
        match = MatchInfo(
            sport="padel",
            court="Court 1",
            time="10:00",
            url="http://example.com/match1",
            is_available=True,
        )
        site_matches = [
            SiteMatches(site=sites[1], date="2024-06-11", distance_km=0.0, matches=[match]),
        ]

        # First call raises exception, second returns data
        mock_scrap_websdepadel_court_data.side_effect = [Exception("Scraper failed"), site_matches]

        response = get_court_data(MatchFilter(days="0", time_min="10:00", time_max="13:00"), sites)

        # Should have data from the second site only
        assert len(response) == 1
        assert response[0].site == sites[1]
        assert len(response[0].matches) == 1
        assert response[0].matches[0].court == "Court 1"
