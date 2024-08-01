from typing import Self

import requests
from bs4 import BeautifulSoup, Tag

from app.cache import cache
from app.integrations.scrapers.scraper_interface import ScrapperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import check_filters, get_weekly_dates, time_not_in_range


class WebsdepadelScrapper(ScrapperInterface):
    BASE_URL = "https://www.{site}/partidas/{date}#contenedor-partidas"

    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        data = []
        for date in get_weekly_dates(filter):
            cache_key = f"{site.url}-{filter.sport}-{filter.is_available}-{date}-{filter.time_min}-{filter.time_max}"
            date_data = []
            if cached_data := cache.get(cache_key):
                data.extend(cached_data)
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
                            date_data.append(match_info)

            cache.set(cache_key, date_data, timeout=1800)
            data.extend(date_data)
        return data
