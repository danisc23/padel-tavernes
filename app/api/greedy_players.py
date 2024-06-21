from flask import Response, jsonify
from flask_restx import Namespace, Resource

from app.api.common import headers_parser
from app.context_helpers import get_sites
from app.models import GreedyPlayersFilter
from app.services.greedy_players import scrap_greedy_players

ns = Namespace(
    "greedy-players", description="Return the list of players that will be playing the most in the next 7 days"
)

greedy_players_parser = headers_parser.copy()
greedy_players_parser.add_argument(
    "sport", type=str, help="filter by sport (padel, tenis..)", location="args", default="padel"
)
greedy_players_parser.remove_argument("X-GEOLOCATION")


@ns.route("/")
class GreedyPlayers(Resource):
    @ns.expect(greedy_players_parser)
    def get(self) -> Response:
        """Return the list of players that will be playing the most in the next 7 days"""
        args = greedy_players_parser.parse_args()
        filter = GreedyPlayersFilter(sport=str(args.get("sport")))
        data = scrap_greedy_players(filter, get_sites())
        return jsonify(data)
