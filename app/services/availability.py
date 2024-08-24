from geopy.distance import distance

from app.integrations.scrapers import SCRAPERS
from app.models import GeolocationFilter, MatchFilter, SiteInfo, SiteMatches


def add_distance_to_site_matches(
    site_match: SiteMatches, geolocation_filter: GeolocationFilter, site: SiteInfo
) -> None:
    site_match.distance_km = distance(
        (geolocation_filter.latitude, geolocation_filter.longitude),
        site.coordinates,
    ).km


def get_court_data(
    filter: MatchFilter, sites: list[SiteInfo], geolocation_filter: GeolocationFilter | None = None
) -> list[SiteMatches]:
    data: list[SiteMatches] = []
    for site in sites:
        site_matches = SCRAPERS[site.type](site, filter).get_site_matches()
        if geolocation_filter:
            for site_match in site_matches:
                add_distance_to_site_matches(site_match, geolocation_filter, site)
        data.extend(site_matches)

    data.sort(key=lambda x: (x.date, x.distance_km))
    return data
