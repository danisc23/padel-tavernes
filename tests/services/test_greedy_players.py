from unittest.mock import Mock, patch

import pytest
from freezegun import freeze_time

from app.models import GreedyPlayersFilter, SiteInfo, SiteType
from app.services.greedy_players import scrap_greedy_players


@freeze_time("2024-06-11")
class TestScrapGreedyPlayers:
    HTML_CONTENT = """
    <div>
        <span class="nick">Player1</span>
        <span class="nick">Player2</span>
        <span class="nick">Player1</span>
        <span class="nick">Club Something</span>
        <span class="nick">Inv. Player</span>
        <span class="nick">Player3</span>
        <span class="nick">Player2</span>
    </div>
    """
    SITE = SiteInfo(name="Site", url="http://example.com", type=SiteType.WEBSDEPADEL)

    @patch("app.services.greedy_players.requests.get")
    def test_scrap_greedy_players(self, mock_requests_get):
        """Returns the list of greedy players filtering out club and invited players."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        greedy_filter = GreedyPlayersFilter(sport="padel", days="0")
        result = scrap_greedy_players(greedy_filter, [self.SITE])

        assert len(result) == 3
        assert result[0]["name"] == "Player1"
        assert result[0]["count"] == 2
        assert result[0]["different_dates"] == 1
        assert result[0]["dates"] == ["2024-06-11"]

        assert result[1]["name"] == "Player2"
        assert result[1]["count"] == 2
        assert result[1]["different_dates"] == 1
        assert result[1]["dates"] == ["2024-06-11"]

        assert result[2]["name"] == "Player3"
        assert result[2]["count"] == 1
        assert result[2]["different_dates"] == 1
        assert result[2]["dates"] == ["2024-06-11"]

    @patch("app.services.greedy_players.requests.get")
    @freeze_time("2024-06-11")
    def test_scrap_greedy_players_date_filter(self, mock_requests_get):
        """Returns the list of greedy players only for the specified days."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = self.HTML_CONTENT
        mock_requests_get.return_value = mock_response

        greedy_filter = GreedyPlayersFilter(sport="padel", days="0")
        result = scrap_greedy_players(greedy_filter, [self.SITE])

        assert len(result) == 3
        assert all(date == "2024-06-11" for date in result[0]["dates"])

    @patch("app.services.greedy_players.requests.get")
    def test_scrap_greedy_players_sorting(self, mock_requests_get):
        """Returns the list of greedy players sorted by count, different_dates, and name."""
        html_content = """
        <div>
            <span class="nick">Player1</span>
            <span class="nick">Player2</span>
            <span class="nick">Player1</span>
            <span class="nick">Player2</span>
            <span class="nick">Player3</span>
            <span class="nick">Player2</span>
        </div>
        """
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = html_content
        mock_requests_get.return_value = mock_response

        greedy_filter = GreedyPlayersFilter(sport="padel", days="0")
        result = scrap_greedy_players(greedy_filter, [self.SITE])

        assert len(result) == 3
        assert result[0]["name"] == "Player2"
        assert result[0]["count"] == 3
        assert result[0]["different_dates"] == 1
        assert result[0]["dates"] == ["2024-06-11"]

        assert result[1]["name"] == "Player1"
        assert result[1]["count"] == 2
        assert result[1]["different_dates"] == 1
        assert result[1]["dates"] == ["2024-06-11"]

        assert result[2]["name"] == "Player3"
        assert result[2]["count"] == 1
        assert result[2]["different_dates"] == 1
        assert result[2]["dates"] == ["2024-06-11"]

    def test_scrap_greedy_players_one_site_limit(self):
        greedy_filter = GreedyPlayersFilter(sport="padel", days="0")
        with pytest.raises(ValueError) as exc_info:
            scrap_greedy_players(greedy_filter, [self.SITE, self.SITE])
        assert str(exc_info.value) == "Please provide only one site by using X-SITE header"

    def test_scrap_greedy_players_unsupported_site_type(self, playtomic_site):
        greedy_filter = GreedyPlayersFilter(sport="padel", days="0")
        with pytest.raises(ValueError) as exc_info:
            scrap_greedy_players(greedy_filter, [playtomic_site])
        assert (
            str(exc_info.value)
            == "Site type playtomic is not supported for greedy players. Currently only websdepadel is supported."
        )
