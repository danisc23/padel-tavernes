import logging

import requests
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
        name="XV Pádel",
        url="xvpadel.com",
        coordinates=(39.455, -0.4364),
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
]

SITES_BY_URL = {site.url: site for site in SUPPORTED_SITES}


def filter_sites_by_distance(sites: list[SiteInfo], geo_filter: GeolocationFilter) -> list[SiteInfo]:
    center = (geo_filter.latitude, geo_filter.longitude)
    return [
        SiteInfo(
            name=site.name,
            url=site.url,
            coordinates=site.coordinates,
            type=site.type,
            distance_km=great_circle(center, site.coordinates).km,
        )
        for site in sites
        if great_circle(center, site.coordinates).km <= geo_filter.radius_km
    ]


def get_playtomic_sites(geo_filter: GeolocationFilter) -> list[SiteInfo]:
    # Call Playtomic API to get the list of sites using the GeolocationFilter
    sites: list[SiteInfo] = []
    request = requests.get(
        (
            "https://playtomic.io/api/v1/tenants?user_id=me&playtomic_status=ACTIVE&with_properties=ALLOWS_CASH_PAYMENT&"
            f"coordinate={geo_filter.latitude}%2C{geo_filter.longitude}&sport_id=PADEL&radius={geo_filter.radius_km}000&size=40"
        )
    )
    try:
        response = request.json()
        for tenant in response:
            name = tenant["tenant_name"]
            url = f"https://playtomic.io/tenant/{tenant['tenant_id']}"
            coordinates = float(tenant["address"]["coordinate"]["lat"]), float(tenant["address"]["coordinate"]["lon"])
            distance_km = great_circle((geo_filter.latitude, geo_filter.longitude), coordinates).km
            sites.append(
                SiteInfo(name=name, url=url, coordinates=coordinates, type=SiteType.PLAYTOMIC, distance_km=distance_km)
            )
    except Exception as e:  # TODO: Specify the exception type + Add lint rule to not use bare except.
        logger.error(f"Error getting Playtomic sites: {e}")
    return sites


def find_site_by_url_or_unknown(url: str) -> SiteInfo:
    # TODO: This should also get the website type as a parameter.
    return SITES_BY_URL.get(url, SiteInfo(name="Unknown", url=url, type=SiteType.WEBSDEPADEL))


def get_available_sites(geo_filter: GeolocationFilter, with_playtomic: bool = True) -> AvailableSitesResponse:
    sites = filter_sites_by_distance(SUPPORTED_SITES, geo_filter) if geo_filter else list(SUPPORTED_SITES)
    sites.extend(get_playtomic_sites(geo_filter))
    return AvailableSitesResponse(sites=sites, last_update="2024-06-20")
