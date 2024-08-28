from flask_restx import Api

from app.api.availability import ns as availability_ns
from app.api.errors import init_error_handlers
from app.api.geolocation import ns as geolocation_ns
from app.api.sites import ns as sites_ns

api = Api(
    title="Padel Court Availability API",
    version="1.0",
    description="API to check padel and tenis courts availability",
    doc="/docs",
)

init_error_handlers(api)
api.add_namespace(availability_ns, path="/api/availability")
api.add_namespace(sites_ns, path="/api/sites")
api.add_namespace(geolocation_ns, path="/api/geolocation")
