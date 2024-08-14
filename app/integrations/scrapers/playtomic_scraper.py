from datetime import datetime, timedelta
from typing import Self

import pytz
import requests

from app.integrations.scrapers.scraper_interface import ScraperInterface
from app.models import MatchFilter, MatchInfo, SiteInfo
from app.services.common import check_filters, get_weekly_dates


class PlaytomicScraper(ScraperInterface):
    BASE_URL = "https://playtomic.io/api/v1/availability"

    def _reduce_results(self: Self, date: str, start_time: str, duration: int, used_start_times: set[str]) -> bool:
        # Artificially reduce the results to only show 90 minutes matches that start at the hour
        match_date = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
        return match_date >= datetime.now() and duration == 90 and start_time not in used_start_times

    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        data = []
        params = {
            "user_id": "me",
            "tenant_id": site.url.split("/")[-1],
            "sport_id": "PADEL",
        }
        court_friendly_name: dict[str, str] = {}
        for date in get_weekly_dates(filter):
            cache_key = self._generate_cache_key(site, filter, date)
            date_data = self._get_cached_data(cache_key)
            if date_data:
                data.extend(date_data)
                continue

            params["local_start_min"] = f"{date}T{filter.time_min}:00"
            params["local_start_max"] = f"{date}T{filter.time_max}:00"
            response = requests.get(self.BASE_URL, params=params)
            if response.status_code != 200:
                continue

            for court in response.json():
                # Assign a friendly name to the court instead of the uuid
                if court["resource_id"] not in court_friendly_name:
                    court_friendly_name[court["resource_id"]] = f"Padel {len(court_friendly_name) + 1}"

                used_start_times: set[str] = set()
                for slot in court["slots"]:
                    if not self._reduce_results(date, slot["start_time"], slot["duration"], used_start_times):
                        continue

                    time = datetime.strptime(slot["start_time"], "%H:%M:%S")
                    used_start_times.add(slot["start_time"])
                    used_start_times.add((time + timedelta(minutes=30)).strftime("%H:%M:%S"))
                    used_start_times.add((time + timedelta(hours=1)).strftime("%H:%M:%S"))

                    # playtomic time is +00:00, so we need to convert it to the local timezone
                    time_utc = pytz.utc.localize(datetime.strptime(f"{date} {slot['start_time']}", "%Y-%m-%d %H:%M:%S"))
                    time_str = time_utc.astimezone(pytz.timezone("Europe/Madrid")).strftime("%H:%M")

                    match_info = MatchInfo(
                        sport="padel",
                        court=court_friendly_name[court["resource_id"]],
                        date=date,
                        time=time_str,
                        url=site.url,
                        is_available=True,
                        site=site,
                    )
                    if check_filters(match_info, filter):
                        date_data.append(match_info)

            self._cache_data(cache_key, date_data)
            data.extend(date_data)

        return data
