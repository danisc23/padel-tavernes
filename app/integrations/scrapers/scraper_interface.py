import logging
from typing import Self

from app.cache import cache
from app.models import MatchFilter, MatchInfo, SiteInfo

logger = logging.getLogger(__name__)


class ScraperInterface:
    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        raise NotImplementedError

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
