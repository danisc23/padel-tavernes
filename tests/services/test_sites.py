from app.models import GeolocationFilter
from app.services.sites import (
    SUPPORTED_SITES,
    find_site_by_url_or_unknown,
    get_available_sites,
)


def test_find_site_by_url_or_unknown_returns_unkown():
    response = find_site_by_url_or_unknown("user_custom_site.com")
    assert response.url == "user_custom_site.com"
    assert response.name == "Unknown"
    assert response.coordinates is None


def test_find_site_by_url_returns_known_site():
    response = find_site_by_url_or_unknown("esportentavernesblanques.es")
    assert response.url == "esportentavernesblanques.es"
    assert response.name == "Esport en Tavernes Blanques"
    assert response.coordinates == (39.5082456, -0.3612918)


def test_get_available_sites_returns_all_sites():
    response = get_available_sites()
    assert len(response.sites) == len(SUPPORTED_SITES)


def test_get_available_sites_filter_by_geolocation():
    geolocation_filter = GeolocationFilter(latitude=39.5082456, longitude=-0.3612918, radius_km=1)
    response = get_available_sites(geolocation_filter)
    assert len(response.sites) == 1

    geolocation_filter = GeolocationFilter(latitude=39.5082456, longitude=-0.3612918, radius_km=10)
    response = get_available_sites(geolocation_filter)
    assert len(response.sites) == 3
