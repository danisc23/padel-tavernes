from flask_restx import Api

from app.api.availability import ns as availability_ns
from app.api.errors import init_error_handlers
from app.api.greedy_players import ns as greedy_players_ns
from app.api.tested_sites import ns as tested_sites_ns

api = Api(
    title="Sports Availability API",
    version="1.0",
    description="API to check padel and tenis courts availability",
    doc="/docs",
)

init_error_handlers(api)

api.add_namespace(availability_ns, path="/api/<string:site>/availability")
api.add_namespace(greedy_players_ns, path="/api/<string:site>/greedy-players")
api.add_namespace(tested_sites_ns, path="/api/tested-sites")
