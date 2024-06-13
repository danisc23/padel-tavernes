from flask import Flask

from app.api.routes import api
from app.middleware import site_middleware


def create_app() -> Flask:
    app = Flask(__name__)
    api.init_app(app)
    app.before_request(site_middleware())
    return app
