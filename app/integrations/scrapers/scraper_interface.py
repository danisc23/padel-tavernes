import logging
from typing import Self

import requests

from app.cache import cache
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteMatches
from app.services.common import get_weekly_dates

logger = logging.getLogger(__name__)


class ScraperInterface:

    def __init__(self, site: SiteInfo, filter: MatchFilter) -> None:
        self.site = site
        self.filter = filter
        self.session = requests.Session()

    def get_site_matches(self: Self) -> list[SiteMatches]:
        site_matches: list[SiteMatches] = []
        try:
            for date in get_weekly_dates(self.filter):
                site_match = SiteMatches(site=self.site, date=date, matches=[])
                cache_key = self._generate_cache_key(self.site, self.filter, date)
                site_match.matches = self._get_cached_data(cache_key)
                if site_match.matches:
                    site_matches.append(site_match)
                    continue

                site_match.matches = self._get_daily_matches(date)

                site_match.matches.sort(key=lambda x: (x.court, x.time))
                self._cache_data(cache_key, site_match.matches)
                if site_match.matches:
                    site_matches.append(site_match)
        finally:
            self.session.close()
        return site_matches

    def _generate_cache_key(self: Self, site: SiteInfo, filter: MatchFilter, date: str) -> str:
        return f"{site.url}-{filter.sport}-{filter.is_available}-{date}-{filter.time_min}-{filter.time_max}"

    def _get_cached_data(self: Self, cache_key: str) -> list[MatchInfo]:
        cached_data = cache.get(cache_key) if cache.get(cache_key) else []
        if len(cached_data) > 0:
            logger.debug(f"Data retrieved from cache with key: {cache_key}")
        return cached_data

    def _cache_data(self: Self, cache_key: str, data: list[MatchInfo]) -> None:
        cache.set(cache_key, data, timeout=1800)
        logger.debug(f"Data cached with key: {cache_key} for 30 minutes")

    def _get_daily_matches(self: Self, date: str) -> list[MatchInfo]:
        raise NotImplementedError
