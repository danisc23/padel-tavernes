from app.models import SiteType

from .matchpoint_scraper import MatchpointScraper
from .playtomic_scraper import PlaytomicScraper
from .scraper_interface import ScraperInterface
from .websdepadel_scraper import WebsdepadelScraper

SCRAPERS: dict[SiteType, type[ScraperInterface]] = {
    SiteType.WEBSDEPADEL: WebsdepadelScraper,
    SiteType.PLAYTOMIC: PlaytomicScraper,
    SiteType.MATCHPOINT: MatchpointScraper,
}
