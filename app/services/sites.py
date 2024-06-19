from geopy.distance import great_circle

from app.models import AvailableSitesResponse, GeolocationFilter, SiteInfo

SUPPORTED_SITES = [
    SiteInfo(
        name="Esport en Tavernes Blanques",
        url="esportentavernesblanques.es",
        coordinates=(39.5082456, -0.3612918),
    ),
    SiteInfo(
        name="Iale Esport",
        url="ialesport.com",
        coordinates=(39.566059, -0.545158),
    ),
    SiteInfo(
        name="Padel Gym Club",
        url="padelgymclub.com",
        coordinates=(39.231919, -0.490272),
    ),
    SiteInfo(
        name="Desafio Pádel",
        url="desafiopadel.com",
        coordinates=(39.478659703180085, -0.4673362596634848),
    ),
    SiteInfo(
        name="XV Pádel",
        url="xvpadel.com",
        coordinates=(39.455, -0.4364),
    ),
    SiteInfo(
        name="XTD Pádel",
        url="padelparccentralxtd.com",
        coordinates=(39.4275981, -0.4651558),
    ),
    SiteInfo(
        name="Muro Club de Tenis y Pádel",
        url="ctplaplana.com",
        coordinates=(38.777681, -0.460267),
    ),
]

SITES_BY_URL = {site.url: site for site in SUPPORTED_SITES}


def find_site_by_url_or_unknown(url: str) -> SiteInfo:
    return SITES_BY_URL.get(url, SiteInfo(name="Unknown", url=url))


def filter_sites_by_distance(sites: list[SiteInfo], geo_filter: GeolocationFilter) -> list[SiteInfo]:
    center = (geo_filter.latitude, geo_filter.longitude)
    return [site for site in sites if great_circle(center, site.coordinates).km <= geo_filter.radius_km]


def get_available_sites(geo_filter: GeolocationFilter | None = None) -> AvailableSitesResponse:
    sites = filter_sites_by_distance(SUPPORTED_SITES, geo_filter) if geo_filter else SUPPORTED_SITES
    return AvailableSitesResponse(sites=sites, last_update="2024-06-15")
