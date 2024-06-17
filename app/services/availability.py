from datetime import datetime

import requests
from bs4 import BeautifulSoup, Tag
from unidecode import unidecode

from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import get_weekly_dates


def check_filters(match_info: MatchInfo, match_filter: MatchFilter) -> bool:
    if match_filter.sport and unidecode(match_filter.sport.lower()) not in unidecode(match_info.sport.lower()):
        return False
    if match_filter.is_available is not None and match_info.is_available != match_filter.is_available:
        return False
    match_datetime = f"{match_info.date} {match_info.time}"
    if match_datetime < datetime.now().strftime("%Y-%m-%d %H:%M"):
        return False
    return True


def scrap_court_data(filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
    data = []
    for date in get_weekly_dates(filter):
        url = f"https://www.{site.url}/partidas/{date}#contenedor-partidas"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        availability = soup.find("div", id="resumen-disponibilidad")
        if not availability or not isinstance(availability, Tag):
            continue

        sports = availability.find_all("li", class_="deporte")
        for sport in sports:
            sport_name = sport.find("span", class_="nombre").get_text(strip=True)
            courts = sport.find_all("li", class_="pista")
            for court in courts:
                court_name = court.find("span", class_="nombre").get_text(strip=True)
                matchs = court.find_all("li", class_="partida")
                for match in matchs:
                    match_info = MatchInfo(
                        sport=sport_name,
                        court=court_name,
                        date=date,
                        time=match.find("a").get_text(strip=True),
                        url=match.find("a")["href"],
                        is_available="partida-reservada" not in match["class"],
                        site=site,
                    )
                    if check_filters(match_info, filter):
                        data.append(match_info)
    return data


def get_court_data(filter: MatchFilter, sites: list[SiteInfo]) -> list[MatchInfo]:
    data: list[MatchInfo] = []
    for site in sites:
        data.extend(scrap_court_data(filter, site))

    data.sort(key=lambda x: (x.date, x.time))
    return data
