from app.integrations.geolocation.geolocation_provider_interface import (
    GeolocationProvider,
)
from app.models import GeolocatedPlace


class GeolocationManager:
    def __init__(self, geolocation_provider: GeolocationProvider):
        self.geolocation_provider = geolocation_provider

    def get_reverse_geolocation(self, latitude: float, longitude: float) -> GeolocatedPlace:
        return self.geolocation_provider.get_reverse_geolocation(latitude, longitude)

    def get_matching_places(self, query_text: str) -> list[GeolocatedPlace]:
        return self.geolocation_provider.get_matching_places(query_text)
