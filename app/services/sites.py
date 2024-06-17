from app.models import AvailableSitesResponse, SiteInfo

SUPPORTED_SITES = [
    SiteInfo(
        name="Esport en Tavernes Blanques",
        url="esportentavernesblanques.es",
        coordinates=(39.494, -0.384),
    ),
    SiteInfo(
        name="Iale Esport",
        url="ialesport.com",
        coordinates=(39.545, -0.461),
    ),
    SiteInfo(
        name="Padel Gym Club",
        url="padelgymclub.com",
        coordinates=(39.476, -0.368),
    ),
    SiteInfo(
        name="Desafio Pádel",
        url="desafiopadel.com",
        coordinates=(39.474, -0.368),
    ),
    SiteInfo(
        name="XV Pádel",
        url="xvpadel.com",
        coordinates=(39.476, -0.368),
    ),
    SiteInfo(
        name="XTD Pádel",
        url="padelparccentralxtd.com",
        coordinates=(39.476, -0.368),
    ),
    SiteInfo(
        name="Muro Club de Tenis y Pádel",
        url="ctplaplana.com",
        coordinates=(39.545, -0.461),
    ),
]

SITES_BY_URL = {site.url: site for site in SUPPORTED_SITES}


def find_site_by_url_or_unknown(url: str) -> SiteInfo:
    return SITES_BY_URL.get(url, SiteInfo(name="Unknown", url=url))


def get_sites() -> AvailableSitesResponse:
    return AvailableSitesResponse(sites=SUPPORTED_SITES, last_update="2024-06-15")
