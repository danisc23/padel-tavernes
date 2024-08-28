import logging

from flask import Flask
from flask_cors import CORS

from app.api.routes import api
from app.cache import cache
from app.middleware import site_middleware
from app.settings import PT_ALLOWED_ORIGINS

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    CORS(app, resources={r"/api/*": {"origins": PT_ALLOWED_ORIGINS}})
    api.init_app(app)
    cache.init_app(app)
    app.before_request(site_middleware())

    return app


app = create_app()
