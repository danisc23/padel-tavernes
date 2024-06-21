from typing import Callable

from flask import g, request

from app.models import GeolocationFilter
from app.services.sites import find_site_by_url_or_unknown, get_available_sites


def site_middleware() -> Callable:
    def middleware() -> None:
        site_url = request.headers.get("X-SITE")
        geo_filter_header = request.headers.get("X-GEOLOCATION")
        if site_url and geo_filter_header:
            raise ValueError("Please provide only one of the following headers: X-SITE or X-GEOLOCATION")
        geo_filter_header = geo_filter_header or "39.469908,-0.376288,100"
        try:
            latitude, longitude, radius = geo_filter_header.split(",")
        except ValueError:
            raise ValueError("Please provide a valid geolocation header with the format: latitude,longitude,radius_km")
        g.geo_filter = GeolocationFilter(latitude=float(latitude), longitude=float(longitude), radius_km=int(radius))
        if site_url:
            g.sites = [find_site_by_url_or_unknown(site_url)]
        elif geo_filter_header:
            g.sites = get_available_sites(g.geo_filter).sites
        else:
            raise ValueError(
                "Please provide a site by using X-SITE header or a geolocation filter by using X-GEOLOCATION header"
            )

    return middleware
