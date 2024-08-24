from typing import Self

import requests
from bs4 import BeautifulSoup, Tag

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteMatches
from app.services.common import (
    check_filters,
    get_weekly_dates,
    time_in_past,
    time_not_in_range,
)


class WebsdepadelScraper(ScraperInterface):
    BASE_URL = "https://www.{site}/partidas/{date}#contenedor-partidas"

    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[SiteMatches]:
        data: list[SiteMatches] = []
        for date in get_weekly_dates(filter):
            site_match = SiteMatches(site=site, date=date, matches=[])
            cache_key = self._generate_cache_key(site, filter, date)
            site_match.matches = self._get_cached_data(cache_key)
            if site_match.matches:
                data.append(site_match)
                continue

            url = self.BASE_URL.format(site=site.url, date=date)
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
                        start_time = match.find("a").get_text(strip=True)
                        if time_not_in_range(start_time, filter) or time_in_past(date, start_time):
                            continue
                        match_info = MatchInfo(
                            sport=sport_name,
                            court=court_name,
                            time=start_time,
                            url=match.find("a")["href"],
                            is_available="partida-reservada" not in match["class"],
                        )
                        if check_filters(match_info, filter):
                            site_match.matches.append(match_info)

            self._cache_data(cache_key, site_match.matches)
            if site_match.matches:
                data.append(site_match)
        return data
