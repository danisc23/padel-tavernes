from flask import Flask

from app.api.routes import api


def create_app() -> Flask:
    app = Flask(__name__)
    api.init_app(app)
    return app
