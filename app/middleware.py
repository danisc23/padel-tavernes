from typing import Callable

from flask import g, request

from app.services.sites import SUPPORTED_SITES, find_site_by_url_or_unknown


def site_middleware() -> Callable:
    def middleware() -> None:
        site_url = request.headers.get("X-SITE")
        g.sites = [find_site_by_url_or_unknown(site_url)] if site_url else SUPPORTED_SITES

    return middleware
