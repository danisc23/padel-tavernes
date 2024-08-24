import pytest
from flask import Flask, g
from flask.testing import FlaskClient

from app.models import GeolocationFilter, SiteType
from app.services.sites import SUPPORTED_SITES


@pytest.fixture
def middleware_client(app: Flask) -> FlaskClient:
    @app.route("/test")
    def test_middlewares():
        return "ok"

    return app.test_client()


def test_middleware_default(mocker, middleware_client):
    mocker.patch("app.services.sites.get_playtomic_sites", return_value=[])
    response = middleware_client.get("/test")
    assert response.text == "ok"
    assert g.geo_filter == GeolocationFilter(latitude=39.469908, longitude=-0.376288, radius_km=100)


def test_site_middleware_custom(middleware_client):
    response = middleware_client.get("/test", headers={"X-SITE": "customsite.com"})
    assert response.text == "ok"
    assert len(g.sites) == 1
    assert g.sites[0].url == "customsite.com"
    assert g.sites[0].name == "Unknown"
    assert g.sites[0].coordinates is None
    assert g.sites[0].type == SiteType.WEBSDEPADEL


def test_geolocation_middleware_custom(mocker, middleware_client, playtomic_site):
    mocker.patch("app.services.sites.get_playtomic_sites", return_value=[playtomic_site])
    response = middleware_client.get("/test", headers={"X-GEOLOCATION": "39.509908,-0.386288,3"})
    assert response.text == "ok"
    assert g.sites == [SUPPORTED_SITES[0], SUPPORTED_SITES[7], playtomic_site]
    assert g.geo_filter == GeolocationFilter(latitude=39.509908, longitude=-0.386288, radius_km=3)


def test_custom_site_and_custom_geolocation_not_allowed(middleware_client):
    with pytest.raises(ValueError) as exc_info:
        middleware_client.get("/test", headers={"X-SITE": "customsite.com", "X-GEOLOCATION": "39.509908,-0.386288,3"})
    assert str(exc_info.value) == "Please provide only one of the following headers: X-SITE or X-GEOLOCATION"


def test_bad_geolocation_header(middleware_client):
    with pytest.raises(ValueError) as exc_info:
        middleware_client.get("/test", headers={"X-GEOLOCATION": "39.509908"})
    assert (
        str(exc_info.value) == "Please provide a valid geolocation header with the format: latitude,longitude,radius_km"
    )

    with pytest.raises(ValueError) as exc_info:
        middleware_client.get("/test", headers={"X-GEOLOCATION": "39.509908,-0.386288,3,4"})
    assert (
        str(exc_info.value) == "Please provide a valid geolocation header with the format: latitude,longitude,radius_km"
    )
