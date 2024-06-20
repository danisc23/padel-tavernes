from flask import Response, jsonify
from flask_caching import Cache
from flask_restx import Namespace, Resource, reqparse

from app import app
from app.api.sites import get_geolocation_filter
from app.context_helpers import get_sites
from app.models import MatchFilter
from app.services.availability import get_court_data
from app.services.sites import filter_sites_by_distance

cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

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
availability_parser.add_argument("latitude", type=float, help="Reference latitude coordinate", location="args")
availability_parser.add_argument("longitude", type=float, help="Reference longitude coordinate", location="args")
availability_parser.add_argument("radius_km", type=int, help="Search radius in km", location="args")


@ns.route("/")
class CourtAvailability(Resource):
    @ns.expect(availability_parser)
    @cache.cached(timeout=1800, query_string=True)
    def get(self) -> Response:
        """See court availability"""
        args = availability_parser.parse_args()
        geolocation_filter = get_geolocation_filter(args.get("latitude"), args.get("longitude"), args.get("radius_km"))
        sites = filter_sites_by_distance(get_sites(), geolocation_filter) if geolocation_filter else get_sites()

        match_filter = MatchFilter(
            sport=args.get("sport"),
            is_available=args.get("is_available"),
            days=args.get("days", "0123456"),
        )
        data = get_court_data(match_filter, sites)
        return jsonify([match.model_dump() for match in data])
