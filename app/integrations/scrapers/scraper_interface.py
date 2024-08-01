from typing import Self

from app.models import MatchFilter, MatchInfo, SiteInfo


class ScrapperInterface:
    def get_court_data(self: Self, filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
        raise NotImplementedError
