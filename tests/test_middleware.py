import pytest
from flask import Flask, g
from flask.testing import FlaskClient

from app.services.sites import SUPPORTED_SITES


@pytest.fixture
def middleware_client(app: Flask) -> FlaskClient:
    @app.route("/test")
    def test_middlewares():
        return "ok"

    return app.test_client()


def test_site_middleware_default(mocker, middleware_client):
    mocker.patch("app.services.sites.get_playtomic_sites", return_value=[])
    response = middleware_client.get("/test")
    assert response.text == "ok"
    assert g.sites == SUPPORTED_SITES


def test_site_middleware_custom(middleware_client):
    response = middleware_client.get("/test", headers={"X-SITE": "customsite.com"})
    assert response.text == "ok"
    assert len(g.sites) == 1
    assert g.sites[0].url == "customsite.com"
    assert g.sites[0].name == "Unknown"
    assert g.sites[0].coordinates is None
