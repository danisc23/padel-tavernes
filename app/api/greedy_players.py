from flask import Response, jsonify
from flask_restx import Namespace, Resource, reqparse

from app.models import GreedyPlayersFilter
from app.services.scrap_greedy_players import scrap_greedy_players

ns = Namespace(
    "greedy-players", description="Return the list of players that will be playing the most in the next 7 days"
)

greedy_players_parser = reqparse.RequestParser()
greedy_players_parser.add_argument(
    "sport", type=str, help="filter by sport (padel, tenis..)", location="args", default="padel"
)


@ns.route("/")
class GreedyPlayers(Resource):
    @ns.expect(greedy_players_parser)
    def get(self, site: str) -> Response:
        """Return the list of players that will be playing the most in the next 7 days"""
        args = greedy_players_parser.parse_args()
        filter = GreedyPlayersFilter(sport=str(args.get("sport")))
        data = scrap_greedy_players(filter, site)
        return jsonify(data)
