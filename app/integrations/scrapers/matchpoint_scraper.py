import logging
import re
import unicodedata
from typing import Self

import requests
from bs4 import BeautifulSoup

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteMatches
from app.services.common import (
    check_filters,
    get_weekly_dates,
    time_in_past,
    time_not_in_range,
)

logger = logging.getLogger(__name__)


class MatchpointScraper(ScraperInterface):
    BASE_URL = "https://{site}/Booking/Grid.aspx"
    SPORTS_URL = "https://{site}/booking/srvc.aspx/ObtenerCuadros"
    BOOKING_URL = "https://{site}/booking/srvc.aspx/ObtenerCuadro"

    def __init__(self) -> None:
        self.session = requests.Session()

    def _get_api_key(self, site: SiteInfo) -> str:
        url = self.BASE_URL.format(site=site.url)
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

        raise ValueError("hl90njda2b89k key not found")

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

    def _get_sport_ids(self, site: SiteInfo, filter: MatchFilter, key: str) -> list[int]:
        url = self.SPORTS_URL.format(site=site.url)
        response = self.session.post(url, json={"key": key})
        response_data = response.json()
        return self._filter_sport_ids(response_data["d"], filter)

    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[SiteMatches]:
        # TODO:
        # - Login may be required for some sites, need to add a prior login step here
        # - Should be able to fetch multiple sports, but we are only fetching the first one, this
        # is because I will limit the api to filter by only one sport in further PRs
        data: list[SiteMatches] = []
        try:
            key = self._get_api_key(site)
            self.session.headers.update(
                {
                    "Referer": self.BASE_URL.format(site=site.url),
                }
            )
            sport_ids = self._get_sport_ids(site, filter, key)
            for date, payload_date in zip(get_weekly_dates(filter), get_weekly_dates(filter, "%d/%m/%Y")):
                site_match = SiteMatches(site=site, date=date, matches=[])
                cache_key = self._generate_cache_key(site, filter, date)
                site_match.matches = self._get_cached_data(cache_key)
                if site_match.matches:
                    data.append(site_match)
                    continue

                url = self.BOOKING_URL.format(site=site.url)
                payload = {"idCuadro": sport_ids[0], "fecha": payload_date, "key": key}
                response = self.session.post(url, json=payload)
                response_data = response.json()
                if "d" not in response_data or "Columnas" not in response_data["d"]:
                    logger.error(f"Columns not found for date {date}, site {site.url}")
                    continue

                courts = response_data["d"]["Columnas"]
                for court in courts:
                    court_name = court["TextoPrincipal"]
                    times = court["HorariosFijos"]
                    for time in times:
                        start_time = time["StrHoraInicio"]
                        if time_not_in_range(start_time, filter) or time_in_past(date, start_time):
                            continue
                        match_info = MatchInfo(
                            sport=filter.sport or "padel",
                            url=self.BASE_URL.format(site=site.url),
                            time=start_time,
                            court=court_name,
                            is_available=True,
                        )
                        if check_filters(match_info, filter):
                            site_match.matches.append(match_info)

                self._cache_data(cache_key, site_match.matches)
                if site_match.matches:
                    data.append(site_match)
        finally:
            self.session.close()
        return data
