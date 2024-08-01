from typing import Self

from app.cache import cache
from app.models import MatchFilter, MatchInfo, SiteInfo


class ScrapperInterface:
    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        raise NotImplementedError

    def _generate_cache_key(self: Self, site: SiteInfo, filter: MatchFilter, date: str) -> str:
        return f"{site.url}-{filter.sport}-{filter.is_available}-{date}-{filter.time_min}-{filter.time_max}"

    def _get_cached_data(self: Self, cache_key: str) -> list[MatchInfo]:
        return cache.get(cache_key) if cache.get(cache_key) else []

    def _cache_data(self: Self, cache_key: str, data: list[MatchInfo]) -> None:
        cache.set(cache_key, data, timeout=1800)
