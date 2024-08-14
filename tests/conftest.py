import socket
from typing import Iterable
from unittest.mock import patch

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app.api.routes import api
from app.middleware import site_middleware
from app.models import SiteInfo, SiteType


def guard(*args, **kwargs):
    raise Exception("Network calls are not allowed in tests")


socket.socket = guard  # type: ignore


@pytest.fixture
def app() -> Iterable[Flask]:
    app = Flask(__name__)
    app.config.update(
        {
            "TESTING": True,
        }
    )
    api.init_app(app)
    app.before_request(site_middleware())

    with app.app_context():
        yield app


@pytest.fixture
def example_site() -> SiteInfo:
    return SiteInfo(url="example.com", name="Example Site", type=SiteType.WEBSDEPADEL)


@pytest.fixture
def playtomic_site() -> SiteInfo:
    return SiteInfo(
        url="playtomic.io/name/uuid", name="Playtomic", type=SiteType.PLAYTOMIC, coordinates=(39.469908, -0.376288)
    )


@pytest.fixture
def client(mocker, app: Flask, playtomic_site: SiteInfo) -> FlaskClient:
    mocker.patch("app.services.sites.get_playtomic_sites", return_value=[])
    return app.test_client()


@pytest.fixture(scope="module")
def patch_cache():
    with (
        patch("app.integrations.scrapers.scraper_interface.cache.get") as mock_cache_get,
        patch("app.integrations.scrapers.scraper_interface.cache.set") as mock_cache_set,
    ):
        mock_cache_get.return_value = None
        yield mock_cache_get, mock_cache_set
