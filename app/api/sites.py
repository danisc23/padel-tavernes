from flask_restx import Namespace, Resource, ValidationError, fields

from app.models import GeolocationFilter
from app.services.sites import get_available_sites

ns = Namespace("tested sites", description="Get the list of supported sites and last update (may be outdated)")

tested_sites_parser = ns.parser()
tested_sites_parser.add_argument("latitude", type=float, help="Reference latitude coordinate", location="args")
tested_sites_parser.add_argument("longitude", type=float, help="Reference longitude coordinate", location="args")
tested_sites_parser.add_argument("radius_km", type=float, help="Search radius in km", location="args")


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
                    },
                )
            )
        ),
        "last_update": fields.String,
    },
)


def get_geolocation_filter(
    latitude: float | None, longitude: float | None, radius_km: float | None
) -> GeolocationFilter | None:
    if type(latitude) is float and type(longitude) is float and type(radius_km) is float:
        return GeolocationFilter(latitude=latitude, longitude=longitude, radius_km=radius_km)

    if any([latitude, longitude, radius_km]):
        raise ValidationError("All of latitude, longitude, and radius_km must be provided together.")

    return None


@ns.route("/")
class AvailableSites(Resource):
    @ns.expect(tested_sites_parser)
    @ns.marshal_with(tested_sites_model)
    def get(self) -> dict:
        """Get the list of supported sites and last update (may be outdated)"""
        args = tested_sites_parser.parse_args()
        latitude: float | None = args.get("latitude")
        longitude = args.get("longitude")
        radius_km = args.get("radius_km")
        geo_filter = get_geolocation_filter(latitude, longitude, radius_km)
        return get_available_sites(geo_filter).model_dump()
