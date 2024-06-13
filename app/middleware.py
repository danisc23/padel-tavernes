from typing import Callable

from flask import g, request


def site_middleware(default_site: str = "esportentavernesblanques.es") -> Callable:
    def middleware() -> None:
        g.site = request.headers.get("X-SITE", default_site)

    return middleware
