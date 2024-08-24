from datetime import datetime, timedelta
from typing import Self

import pytz

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import check_filters


class PlaytomicScraper(ScraperInterface):
    BASE_URL = "https://playtomic.io/api/v1/availability"

    def __init__(self, site: SiteInfo, filter: MatchFilter) -> None:
        super().__init__(site, filter)
        self.court_friendly_names: dict[str, str] = {}

    def _reduce_results(self: Self, date: str, start_time: str, duration: int, used_start_times: set[str]) -> bool:
        # Artificially reduce the results to only show 90 minutes matches that start at the hour
        match_date = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
        return match_date >= datetime.now() and duration == 90 and start_time not in used_start_times

    def _localize_time(self: Self, date: str, start_time: str) -> str:
        time_utc = pytz.utc.localize(datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S"))
        return time_utc.astimezone(pytz.timezone("Europe/Madrid")).strftime("%H:%M")

    def _friendly_court_name(self: Self, court_id: str) -> str:
        if court_id not in self.court_friendly_names:
            self.court_friendly_names[court_id] = f"Padel {len(self.court_friendly_names) + 1}"
        return self.court_friendly_names[court_id]

    def _get_scraped_availability(self: Self, date: str) -> list[dict]:
        params = {
            "user_id": "me",
            "tenant_id": self.site.url.split("/")[-1],
            "sport_id": "PADEL",
            "local_start_min": f"{date}T{self.filter.time_min}:00",
            "local_start_max": f"{date}T{self.filter.time_max}:00",
        }

        response = self.session.get(self.BASE_URL, params=params)
        if response.status_code != 200:
            return []

        return response.json()

    def _get_daily_matches(self: Self, date: str) -> list[MatchInfo]:
        data: list[MatchInfo] = []

        courts = self._get_scraped_availability(date)
        for court in courts:

            used_start_times: set[str] = set()
            for match in court["slots"]:
                if not self._reduce_results(date, match["start_time"], match["duration"], used_start_times):
                    continue

                time = datetime.strptime(match["start_time"], "%H:%M:%S")
                used_start_times.add(match["start_time"])
                used_start_times.add((time + timedelta(minutes=30)).strftime("%H:%M:%S"))
                used_start_times.add((time + timedelta(hours=1)).strftime("%H:%M:%S"))

                match_info = MatchInfo(
                    sport="padel",
                    court=self._friendly_court_name(court["resource_id"]),
                    time=self._localize_time(date, match["start_time"]),
                    url=self.site.url,
                    is_available=True,
                )
                if check_filters(match_info, self.filter):
                    data.append(match_info)

        return data
