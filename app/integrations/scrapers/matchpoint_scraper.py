import logging
import re
import unicodedata
from datetime import datetime
from typing import Self

from bs4 import BeautifulSoup

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import check_filters, time_in_past, time_not_in_range

logger = logging.getLogger(__name__)


class MatchpointScraper(ScraperInterface):
    BASE_URL = "https://{site}/Booking/Grid.aspx"
    SPORTS_URL = "https://{site}/booking/srvc.aspx/ObtenerCuadros"
    BOOKING_URL = "https://{site}/booking/srvc.aspx/ObtenerCuadro"

    def __init__(self, site: SiteInfo, filter: MatchFilter) -> None:
        super().__init__(site, filter)
        self.session.headers.update(
            {
                "Referer": self.BASE_URL.format(site=site.url),
            }
        )
        self.key = self._get_api_key()
        self.sport_ids = self._get_sport_ids()

    def _get_api_key(self) -> str:
        url = self.BASE_URL.format(site=self.site.url)
        response = self.session.get(url)
        html_content = response.text
        soup = BeautifulSoup(html_content, "html.parser")

        scripts = soup.find_all("script")
        for script in scripts:
            if "hl90njda2b89k" in script.text:
                match = re.search(r"hl90njda2b89k\s*=\s*'([^']+)'", script.text)
                if match:
                    api_key = match.group(1)
                    return api_key

        logger.error("hl90njda2b89k key not found")
        return ""

    def _filter_sport_ids(self, sports: list[dict], filter: MatchFilter) -> list[int]:
        sport_ids = []
        if not filter.sport:
            return [sport["Id"] for sport in sports]
        for sport in sports:
            if (
                filter.sport
                and filter.sport.lower()
                in unicodedata.normalize("NFKD", sport["Nombre"]).encode("ASCII", "ignore").decode("utf-8").lower()
            ):
                sport_ids.append(sport["Id"])
        return sport_ids

    def _get_sport_ids(self) -> list[int]:
        url = self.SPORTS_URL.format(site=self.site.url)
        response = self.session.post(url, json={"key": self.key})
        response_data = response.json()
        return self._filter_sport_ids(response_data["d"], self.filter)

    def _get_scraped_availability(self: Self, date: str) -> list[dict]:
        if not self.sport_ids:
            logger.info(f"No sport id found for site {self.site.url}")
            return []

        url = self.BOOKING_URL.format(site=self.site.url)
        payload_date = datetime.strptime(date, "%Y-%m-%d").strftime("%d/%m/%Y")
        payload = {"idCuadro": self.sport_ids[0], "fecha": payload_date, "key": self.key}
        response = self.session.post(url, json=payload)
        response_data = response.json()

        if "d" not in response_data or "Columnas" not in response_data["d"]:
            logger.error(f"Columns not found for date {date}, site {self.site.url}")
            return []

        return response_data["d"]["Columnas"]

    def _get_daily_matches(self: Self, date: str) -> list[MatchInfo]:
        data: list[MatchInfo] = []

        courts = self._get_scraped_availability(date)
        for court in courts:
            court_name = court["TextoPrincipal"]
            matches = court["HorariosFijos"]
            for match in matches:
                start_time = match["StrHoraInicio"]
                if time_not_in_range(start_time, self.filter) or time_in_past(date, start_time):
                    continue
                match_info = MatchInfo(
                    sport=self.filter.sport or "padel",
                    url=self.BASE_URL.format(site=self.site.url),
                    time=start_time,
                    court=court_name,
                    is_available=True,
                )
                if check_filters(match_info, self.filter):
                    data.append(match_info)

        return data
