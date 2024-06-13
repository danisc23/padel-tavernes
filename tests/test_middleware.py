import pytest
from flask import Flask, g, jsonify
from flask.testing import FlaskClient


@pytest.fixture
def client_site(app: Flask) -> FlaskClient:
    @app.route("/site")
    def get_site():
        return jsonify({"site": g.site})

    return app.test_client()


def test_site_middleware_default(client_site):
    response = client_site.get("/site")
    assert response.json["site"] == "esportentavernesblanques.es"


def test_site_middleware_custom(client_site):
    response = client_site.get("/site", headers={"X-SITE": "customsite.com"})
    assert response.json["site"] == "customsite.com"
