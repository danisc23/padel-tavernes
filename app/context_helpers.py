from typing import cast

from flask import g

from app.models import SiteInfo


def get_sites() -> list[SiteInfo]:
    # This function is used to get the sites from the global context typed correctly
    # since the global context is not typed by default.
    return cast(list[SiteInfo], g.sites)
