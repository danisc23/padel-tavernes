from app.integrations.scrapers import SCRAPPERS
from app.models import MatchFilter, MatchInfo, SiteInfo


def get_court_data(filter: MatchFilter, sites: list[SiteInfo]) -> list[MatchInfo]:
    data: list[MatchInfo] = []
    for site in sites:
        data.extend(SCRAPPERS[site.type]().get_court_data(filter, site))

    data.sort(key=lambda x: (x.date, x.time))
    return data
