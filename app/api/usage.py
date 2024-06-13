from flask import g
from flask_restx import Namespace, Resource, fields

from app.models import MatchFilter
from app.services.usage import get_court_usage

ns = Namespace("usage", description="See sport and courts usage information")


court_model = ns.model(
    "CourtUsage",
    {
        "name": fields.String(description="The name of the court"),
        "total_booked": fields.Integer(description="Total booked matches"),
        "total_available": fields.Integer(description="Total available matches"),
        "total_matches": fields.Integer(description="Total matches"),
        "booked_percentage": fields.Float(description="Percentage of used matches"),
    },
)

sport_model = ns.model(
    "SportUsage",
    {
        "name": fields.String(description="The name of the sport"),
        "total_booked": fields.Integer(description="Total booked matches for the sport"),
        "total_available": fields.Integer(description="Total available matches for the sport"),
        "total_matches": fields.Integer(description="Total matches for the sport"),
        "booked_percentage": fields.Float(description="Percentage of used matches for the sport"),
        "courts": fields.List(fields.Nested(court_model)),
    },
)

response_model = ns.model(
    "UsageResponse",
    {
        "sports": fields.List(fields.Nested(sport_model)),
        "total_booked": fields.Integer(description="Total booked matches overall"),
        "total_available": fields.Integer(description="Total available matches overall"),
        "total_matches": fields.Integer(description="Total matches overall"),
        "booked_percentage": fields.Float(description="Percentage of used matches overall"),
    },
)

usage_parser = ns.parser()
usage_parser.add_argument("sport", type=str, help="filter by sport, (padel, tenis...)", location="args")
usage_parser.add_argument(
    "days",
    type=str,
    help="weekdays (0123456) being 0=Today and n=Days after today",
    location="args",
    default="0123456",
)


@ns.route("/")
class SportUsage(Resource):
    @ns.expect(usage_parser)
    @ns.marshal_with(response_model)
    def get(self) -> dict:
        """See sport usage"""
        args = usage_parser.parse_args()
        filter = MatchFilter(sport=args.get("sport"), days=args.get("days", "0123456"))
        data = get_court_usage(filter, g.site).model_dump()
        for sport in data["sports"]:
            for court in sport["courts"]:
                court.pop("matches")
        return data
