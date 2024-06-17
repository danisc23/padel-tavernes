from typing import Iterable

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app
from app.middleware import site_middleware
from app.models import SiteInfo


@pytest.fixture
def app() -> Iterable[Flask]:
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )
    app.before_request(site_middleware())

    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()


@pytest.fixture
def example_site() -> SiteInfo:
    return SiteInfo(url="example.com", name="Example Site")
