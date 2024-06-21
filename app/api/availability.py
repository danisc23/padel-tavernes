from flask import Response, jsonify
from flask_caching import Cache
from flask_restx import Namespace, Resource

from app import app
from app.api.common import headers_parser
from app.context_helpers import get_sites
from app.models import MatchFilter
from app.services.availability import get_court_data

cache = Cache(app, config={"CACHE_TYPE": "SimpleCache"})

ns = Namespace("availability", description="See court availability")

availability_parser = headers_parser.copy()
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


def get_cache_availabilty_key() -> str:
    args = availability_parser.parse_args()
    return f"{args.get('sport')}-{args.get('is_available')}-{args.get('days')}-{args.get('X-SITE')}-{args.get('X-GEOLOCATION')}"


@ns.route("/")
class CourtAvailability(Resource):
    @ns.expect(availability_parser)
    @cache.cached(timeout=1800, key_prefix=get_cache_availabilty_key)  # type: ignore
    def get(self) -> Response:
        """See court availability"""
        args = availability_parser.parse_args()

        match_filter = MatchFilter(
            sport=args.get("sport"),
            is_available=args.get("is_available"),
            days=args.get("days", "0123456"),
        )
        data = get_court_data(match_filter, get_sites())
        return jsonify([match.model_dump() for match in data])
