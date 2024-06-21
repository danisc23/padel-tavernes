from typing import cast

from flask import g

from app.models import GeolocationFilter, SiteInfo


def get_sites() -> list[SiteInfo]:
    # This function is used to get the sites from the global context typed correctly
    # since the global context is not typed by default.
    return cast(list[SiteInfo], g.sites)


def get_geo_filter() -> GeolocationFilter:
    # This function is used to get the geo filter from the global context typed correctly
    # since the global context is not typed by default.
    return cast(GeolocationFilter, g.geo_filter)
