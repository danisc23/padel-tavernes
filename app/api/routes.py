from flask_restx import Api

from app.api.availability import ns as availability_ns
from app.api.errors import init_error_handlers
from app.api.greedy_players import ns as greedy_players_ns
from app.api.sites import ns as sites_ns
from app.api.usage import ns as usage_ns

authorizations = {
    "CustomWebsite": {
        "type": "apiKey",
        "in": "header",
        "name": "X-SITE",
        "description": "Optional header to specify the site. Default: All known sites. Take into account that some endpoints only support one site, e.g. ialesport.com",
    }
}
api = Api(
    title="Padel Court Availability API",
    version="1.0",
    description="API to check padel and tenis courts availability",
    doc="/docs",
    authorizations=authorizations,
    security="CustomWebsite",
)

init_error_handlers(api)
api.add_namespace(availability_ns, path="/api/availability")
api.add_namespace(usage_ns, path="/api/usage")
api.add_namespace(greedy_players_ns, path="/api/greedy-players")
api.add_namespace(sites_ns, path="/api/available-sites")
