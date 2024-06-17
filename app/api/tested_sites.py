from flask import Response, jsonify
from flask_restx import Namespace, Resource

from app.services.sites import get_sites

ns = Namespace("tested sites", description="Get the list of supported sites and last update (may be outdated)")


@ns.route("/")
class TestedSites(Resource):
    def get(self) -> Response:
        """Get the list of supported sites and last update (may be outdated)"""
        return jsonify(get_sites().model_dump())
