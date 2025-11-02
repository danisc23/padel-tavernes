import logging

from geopy.distance import great_circle

from app.models import AvailableSitesResponse, GeolocationFilter, SiteInfo, SiteType

logger = logging.getLogger(__name__)

SUPPORTED_SITES = [
    # Webs de Padel Sites
    SiteInfo(
        name="Esport en Tavernes Blanques",
        url="esportentavernesblanques.es",
        coordinates=(39.5082456, -0.3612918),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="Iale Esport",
        url="ialesport.com",
        coordinates=(39.566059, -0.545158),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="Padel Gym Club",
        url="padelgymclub.com",
        coordinates=(39.231919, -0.490272),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="Desafio Pádel",
        url="desafiopadel.com",
        coordinates=(39.478659703180085, -0.4673362596634848),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="XTD Pádel",
        url="padelparccentralxtd.com",
        coordinates=(39.4275981, -0.4651558),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="Muro Club de Tenis y Pádel",
        url="ctplaplana.com",
        coordinates=(38.777681, -0.460267),
        type=SiteType.WEBSDEPADEL,
    ),
    SiteInfo(
        name="BonPadel",
        url="bonpadel.matchpoint.com.es",
        coordinates=(39.515722, -0.3685954),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="Padel Interclub Meliana",
        url="www.padelinterclub.com",
        coordinates=(39.5246497, -0.3543332),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="La Pobla Indoor",
        url="padellapoblaindoor.matchpoint.com.es",
        coordinates=(39.5846443, -0.3224196),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="Padel 365",
        url="padel365.matchpoint.com.es",
        coordinates=(39.5868444, -0.5383648),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="Valencia Tenis Center",
        url="valenciateniscenter.matchpoint.com.es",
        coordinates=(39.4801408, -0.3323505),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="Padel Indoor X3",
        url="x3padel.matchpoint.com.es",
        coordinates=(37.9264372, -1.1721104),
        type=SiteType.MATCHPOINT,
    ),
    SiteInfo(
        name="One Padel Valencia",
        url="onepadelvalencia.matchpoint.com.es",
        coordinates=(39.5188506, -0.4612779),
        type=SiteType.MATCHPOINT,
    ),
]

SITES_BY_URL = {site.url: site for site in SUPPORTED_SITES}


def filter_sites_by_distance(sites: list[SiteInfo], geo_filter: GeolocationFilter) -> list[SiteInfo]:
    center = (geo_filter.latitude, geo_filter.longitude)
    return [site for site in sites if great_circle(center, site.coordinates).km <= geo_filter.radius_km]


def find_site_by_url_or_unknown(url: str) -> SiteInfo:
    # TODO: This should also get the website type as a parameter.
    return SITES_BY_URL.get(url, SiteInfo(name="Unknown", url=url, type=SiteType.WEBSDEPADEL))


def get_available_sites(geo_filter: GeolocationFilter) -> AvailableSitesResponse:
    sites = filter_sites_by_distance(SUPPORTED_SITES, geo_filter) if geo_filter else list(SUPPORTED_SITES)
    return AvailableSitesResponse(sites=sites, last_update="2024-06-20")
