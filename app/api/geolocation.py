import logging

from flask_restx import Namespace, Resource, fields, reqparse

from app.cache import cache
from app.integrations.geolocation.location_iq import LocationIQProvider
from app.services.geolocation import GeolocationManager

logger = logging.getLogger(__name__)

ns = Namespace("geolocation", description="Geolocation related operations")

geolocated_place_model = ns.model(
    "GeolocatedPlace",
    {
        "place_id": fields.String,
        "display_name": fields.String,
        "lat": fields.Float,
        "lon": fields.Float,
    },
)

reverse_geolocation_parser = reqparse.RequestParser()
reverse_geolocation_parser.add_argument("latitude", type=float, required=True, help="Latitude of the location")
reverse_geolocation_parser.add_argument("longitude", type=float, required=True, help="Longitude of the location")

matching_places_parser = reqparse.RequestParser()
matching_places_parser.add_argument("query", type=str, required=True, help="Query text to search for matching places")


def cache_key_for_reverse_geolocation() -> str:
    args = reverse_geolocation_parser.parse_args()
    latitude = str(args.get("latitude"))
    longitude = str(args.get("longitude"))
    return f"reverse_geolocation-{latitude}-{longitude}"


def cache_key_for_matching_places() -> str:
    args = matching_places_parser.parse_args()
    query_text = str(args.get("query")).lower()
    return f"matching_places-{query_text}"


@ns.route("/reverse-geolocation/")
class ReverseGeolocation(Resource):
    @cache.cached(timeout=86400, key_prefix=cache_key_for_reverse_geolocation)
    @ns.expect(reverse_geolocation_parser)
    @ns.marshal_with(geolocated_place_model)
    def get(self) -> dict:
        """Get the geolocation details for a given latitude and longitude"""
        args = reverse_geolocation_parser.parse_args()
        latitude = args.get("latitude")
        longitude = args.get("longitude")

        geolocation_manager = GeolocationManager(LocationIQProvider())
        result = geolocation_manager.get_reverse_geolocation(latitude, longitude)  # type: ignore

        return result.model_dump()


@ns.route("/matching-places/")
class MatchingPlaces(Resource):
    @cache.cached(timeout=86400, key_prefix=cache_key_for_matching_places)
    @ns.expect(matching_places_parser)
    @ns.marshal_with(geolocated_place_model, as_list=True)
    def get(self) -> list:
        """Get a list of places that match the given query text"""
        args = matching_places_parser.parse_args()
        query_text = args.get("query")

        geolocation_manager = GeolocationManager(LocationIQProvider())
        result = geolocation_manager.get_matching_places(query_text)  # type: ignore

        return result
