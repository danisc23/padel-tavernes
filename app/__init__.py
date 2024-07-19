import logging
import os

from flask import Flask
from flask_cors import CORS

from app.api.routes import api
from app.cache import cache
from app.middleware import site_middleware

logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)


def create_app() -> Flask:
    app = Flask(__name__)
    origins = ["*"] if os.getenv("PT_ENV") == "dev" else os.getenv("PT_ALLOWED_ORIGINS", "").split(",")
    if len(origins) == 1 and origins[0] == "":
        logger.warning("No allowed origins set, CORS disabled")
    else:
        CORS(app, resources={r"/api/*": {"origins": origins}})
        logger.info(f"Allowed origins: {origins}")
    api.init_app(app)
    cache.init_app(app)
    app.before_request(site_middleware())

    return app


app = create_app()
