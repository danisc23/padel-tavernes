from flask import Response
from flask.testing import FlaskClient

from app.api.tested_sites import SUPPORTED_SITES


def test_get_returns_response(client: FlaskClient) -> None:
    response = client.get("/api/tested-sites/")
    assert isinstance(response, Response)


def test_get_returns_json_response_with_supported_sites_and_last_update(client: FlaskClient) -> None:
    response = client.get("/api/tested-sites/")
    json_data = response.get_json()

    assert isinstance(json_data, dict)
    assert "sites" in json_data
    assert "last_update" in json_data
    assert json_data["sites"] == SUPPORTED_SITES
    assert json_data["last_update"] == "2024-06-11"
