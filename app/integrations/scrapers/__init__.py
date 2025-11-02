from app.models import SiteType

from .matchpoint_scraper import MatchpointScraper
from .scraper_interface import ScraperInterface
from .websdepadel_scraper import WebsdepadelScraper

SCRAPERS: dict[SiteType, type[ScraperInterface]] = {
    SiteType.WEBSDEPADEL: WebsdepadelScraper,
    SiteType.MATCHPOINT: MatchpointScraper,
}
