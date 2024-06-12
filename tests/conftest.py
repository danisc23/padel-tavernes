from typing import Iterable

import pytest
from flask import Flask
from flask.testing import FlaskClient

from app import create_app


@pytest.fixture
def app() -> Iterable:
    app = create_app()
    app.config.update(
        {
            "TESTING": True,
        }
    )

    with app.app_context():
        yield app


@pytest.fixture
def client(app: Flask) -> FlaskClient:
    return app.test_client()
