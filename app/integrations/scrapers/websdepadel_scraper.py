from typing import Self

import requests
from bs4 import BeautifulSoup, Tag

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import check_filters, get_weekly_dates, time_not_in_range


class WebsdepadelScraper(ScraperInterface):
    BASE_URL = "https://www.{site}/partidas/{date}#contenedor-partidas"

    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        data = []
        for date in get_weekly_dates(filter):
            cache_key = self._generate_cache_key(site, filter, date)
            daily_matches = self._get_cached_data(cache_key)
            if daily_matches:
                data.extend(daily_matches)
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
                        time = match.find("a").get_text(strip=True)
                        if time_not_in_range(time, filter.time_min, filter.time_max):
                            continue
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
                            daily_matches.append(match_info)

            self._cache_data(cache_key, daily_matches)
            data.extend(daily_matches)
        return data
