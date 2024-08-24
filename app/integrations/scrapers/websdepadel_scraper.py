from typing import Self

from bs4 import BeautifulSoup, Tag

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchInfo
from app.services.common import check_filters, time_in_past, time_not_in_range


class WebsdepadelScraper(ScraperInterface):
    BASE_URL = "https://www.{site}/partidas/{date}#contenedor-partidas"

    def _get_scraped_availability(self: Self, date: str) -> Tag | None:
        url = self.BASE_URL.format(site=self.site.url, date=date)
        response = self.session.get(url)
        soup = BeautifulSoup(response.text, "html.parser")
        availability = soup.find("div", id="resumen-disponibilidad")

        return availability if isinstance(availability, Tag) else None

    def _get_daily_matches(self: Self, date: str) -> list[MatchInfo]:
        data: list[MatchInfo] = []

        availability = self._get_scraped_availability(date)

        sports = availability.find_all("li", class_="deporte") if availability else []
        for sport in sports:
            sport_name = sport.find("span", class_="nombre").get_text(strip=True)
            courts = sport.find_all("li", class_="pista")
            for court in courts:
                court_name = court.find("span", class_="nombre").get_text(strip=True)
                matches = court.find_all("li", class_="partida")
                for match in matches:
                    start_time = match.find("a").get_text(strip=True)
                    if time_not_in_range(start_time, self.filter) or time_in_past(date, start_time):
                        continue
                    match_info = MatchInfo(
                        sport=sport_name,
                        court=court_name,
                        time=start_time,
                        url=match.find("a")["href"],
                        is_available="partida-reservada" not in match["class"],
                    )
                    if check_filters(match_info, self.filter):
                        data.append(match_info)

        return data
