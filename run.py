from app import app
from app.api.routes import api
from app.middleware import site_middleware

if __name__ == "__main__":
    api.init_app(app)
    app.before_request(site_middleware())
    app.run(debug=True, port=8000)
