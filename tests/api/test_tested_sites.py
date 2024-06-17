from flask import Response
from flask.testing import FlaskClient

from app.services.sites import get_sites


def test_get_returns_response(client: FlaskClient) -> None:
    response = client.get("/api/tested-sites/")
    assert isinstance(response, Response)


def test_get_returns_json_response_with_supported_sites_and_last_update(client: FlaskClient) -> None:
    response = client.get("/api/tested-sites/")
    json_data = response.get_json()

    assert sorted(json_data) == sorted(get_sites().model_dump())
