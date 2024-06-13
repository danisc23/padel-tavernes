from collections import defaultdict

import requests
from bs4 import BeautifulSoup

from app.models import GreedyPlayerInfo, GreedyPlayersFilter
from app.services.common import get_weekly_dates


def scrap_greedy_players(filter: GreedyPlayersFilter, site: str) -> list:
    player_dict: dict = defaultdict(GreedyPlayerInfo)
    for date in get_weekly_dates(filter):
        url = f"https://www.{site}/partidas/{filter.sport}/{date}"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        all_players = soup.find_all("span", class_="nick")
        players = [player for player in all_players if "Club " not in player.text and "Inv. " not in player.text]
        for player in players:
            player_name = player.get_text(strip=True)
            player_dict[player_name].name = player_name
            player_dict[player_name].count += 1
            player_dict[player_name].dates.add(date)

    greedy_players = [
        {
            "name": player.name,
            "count": player.count,
            "different_dates": player.different_dates,
            "dates": sorted(list(player.dates)),
        }
        for player in player_dict.values()
    ]
    greedy_players.sort(key=lambda x: (-x["count"], -x["different_dates"], x["name"]))
    return greedy_players
