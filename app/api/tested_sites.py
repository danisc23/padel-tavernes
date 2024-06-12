from flask import Response, jsonify
from flask_restx import Namespace, Resource

SUPPORTED_SITES = [
    "esportentavernesblanques.es",
    "ialesport.com",
    "padelgymclub.com",  # greedy players not supported
]

ns = Namespace("tested sites", description="Get the list of supported sites and last update (may be outdated)")


@ns.route("/")
class TestedSites(Resource):
    def get(self) -> Response:
        """Get the list of supported sites and last update (may be outdated)"""
        return jsonify(
            {
                "sites": SUPPORTED_SITES,
                "last_update": "2024-06-11",
            }
        )
