from datetime import datetime, timedelta

from flask_restx import Namespace, Resource, fields, inputs

from app.api.common import headers_parser
from app.context_helpers import get_sites
from app.models import MatchFilter
from app.services.availability import get_court_data

ns = Namespace("availability", description="See court availability")

site_info_model = ns.model(
    "SiteInfo",
    {
        "name": fields.String,
        "url": fields.String,
        "type": fields.String,
        "coordinates": fields.List(fields.Float),
    },
)

match_info_model = ns.model(
    "MatchInfo",
    {
        "sport": fields.String,
        "court": fields.String,
        "date": fields.String,
        "time": fields.String,
        "url": fields.String,
        "is_available": fields.Boolean,
        "site": fields.Nested(site_info_model),
    },
)

availability_parser = headers_parser.copy()
availability_parser.add_argument("sport", type=str, help="filter by sport, (padel, tenis...)", location="args")
availability_parser.add_argument(
    "is_available", type=inputs.boolean, help="see courts available or not available for booking", location="args"
)
availability_parser.add_argument(
    "days",
    type=str,
    help="weekdays (0123456) being 0=Today and n=Days after today, max 3 digits, default=012",
    location="args",
    default="012",
)
availability_parser.add_argument("time_min", type=str, help="minimum time to filter in format HH:MM", location="args")
availability_parser.add_argument(
    "time_max", type=str, help="maximum time to filter in format HH:MM, max 3 hours later", location="args"
)


@ns.route("/")
class CourtAvailability(Resource):
    @ns.expect(availability_parser)
    @ns.marshal_list_with(match_info_model)
    def get(self) -> list:
        """See court availability"""
        args = availability_parser.parse_args()
        current_time = datetime.now()
        three_hours_later = current_time + timedelta(hours=3)
        time_min_str = args.get("time_min") or current_time.strftime("%H:%M")
        time_max_str = args.get("time_max") or three_hours_later.strftime("%H:%M")

        match_filter = MatchFilter(
            sport=args.get("sport"),
            is_available=args.get("is_available"),
            days=args.get("days", "012"),
            time_min=time_min_str,
            time_max=time_max_str,
        )
        data = get_court_data(match_filter, get_sites())
        return [match.model_dump() for match in data]
