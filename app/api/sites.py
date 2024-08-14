from flask_restx import Namespace, Resource, fields

from app.api.common import headers_parser
from app.context_helpers import get_geo_filter
from app.services.sites import get_available_sites

ns = Namespace("sites", description="Get the list of supported sites and last update (may be outdated)")

tested_sites_model = ns.model(
    "TestedSites",
    {
        "sites": fields.List(
            fields.Nested(
                ns.model(
                    "SiteInfo",
                    {
                        "name": fields.String,
                        "url": fields.String,
                        "coordinates": fields.List(fields.Float),
                        "type": fields.String,
                    },
                )
            )
        ),
        "last_update": fields.String,
    },
)


@ns.route("/")
class AvailableSites(Resource):
    @ns.expect(headers_parser)
    @ns.marshal_with(tested_sites_model)
    def get(self) -> dict:
        """Get the list of supported sites and last update (may be outdated)"""
        return get_available_sites(get_geo_filter()).model_dump()
