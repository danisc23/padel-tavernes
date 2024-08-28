from abc import ABC, abstractmethod

from app.models import GeolocatedPlace


class GeolocationProvider(ABC):
    @abstractmethod
    def get_reverse_geolocation(self, latitude: float, longitude: float) -> GeolocatedPlace:
        pass

    @abstractmethod
    def get_matching_places(self, query_text: str) -> list[GeolocatedPlace]:
        pass
