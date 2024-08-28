import logging

import requests

from app.integrations.geolocation.geolocation_provider_interface import (
    GeolocationProvider,
)
from app.models import GeolocatedPlace
from app.settings import LOCATION_IQ_API_KEY

logger = logging.getLogger(__name__)


class LocationIQProvider(GeolocationProvider):
    BASE_URL = "https://eu1.locationiq.com/v1"
    BASE_QUERY_PARAMS = {"key": LOCATION_IQ_API_KEY, "format": "json", "countrycodes": "es"}

    def _map_response_place_to_geolocated_place(self, response_place: dict) -> GeolocatedPlace:
        return GeolocatedPlace(
            place_id=response_place["place_id"],
            display_name=response_place["display_name"],
            lat=response_place["lat"],
            lon=response_place["lon"],
        )

    def _handle_get_response(self, url: str, params: dict) -> list:
        response = requests.get(url, params={**self.BASE_QUERY_PARAMS, **params})
        try:
            response.raise_for_status()
            json_response = response.json()
            if isinstance(json_response, list):
                return json_response
            elif isinstance(json_response, dict):
                return [json_response]
            else:
                logger.error(f"Unexpected response from {url}: {json_response}")
                raise requests.exceptions.RequestException(f"Unexpected response from {url}: {json_response}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Error getting response from {url}: {e}")
            return []

    def get_reverse_geolocation(self, latitude: float, longitude: float) -> GeolocatedPlace:
        url = f"{self.BASE_URL}/reverse.php"
        [response] = self._handle_get_response(
            url,
            params={
                "lat": latitude,
                "lon": longitude,
            },
        )
        return self._map_response_place_to_geolocated_place(response)

    def get_matching_places(self, query_text: str) -> list[GeolocatedPlace]:
        url = f"{self.BASE_URL}/autocomplete.php"
        response = self._handle_get_response(url, params={"q": query_text, "limit": 6})
        return [self._map_response_place_to_geolocated_place(place) for place in response]
