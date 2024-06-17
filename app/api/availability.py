from flask import Response, g, jsonify
from flask_restx import Namespace, Resource, reqparse

from app.models import MatchFilter
from app.services.availability import get_court_data

ns = Namespace("availability", description="See court availability")

availability_parser = reqparse.RequestParser()
availability_parser.add_argument("sport", type=str, help="filter by sport, (padel, tenis...)", location="args")
availability_parser.add_argument(
    "is_available", type=bool, help="see courts available or not available for booking", location="args"
)
availability_parser.add_argument(
    "days",
    type=str,
    help="weekdays (0123456) being 0=Today and n=Days after today",
    location="args",
    default="0123456",
)


@ns.route("/")
class CourtAvailability(Resource):
    @ns.expect(availability_parser)
    def get(self) -> Response:
        """See court availability"""
        args = availability_parser.parse_args()
        filter = MatchFilter(
            sport=args.get("sport"),
            is_available=args.get("is_available"),
            days=args.get("days", "0123456"),
        )
        data = get_court_data(filter, g.sites)
        return jsonify([match.model_dump() for match in data])
