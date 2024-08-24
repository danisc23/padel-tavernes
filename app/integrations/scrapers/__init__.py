from app.models import SiteType

from .matchpoint_scraper import MatchpointScraper
from .playtomic_scraper import PlaytomicScraper
from .websdepadel_scraper import WebsdepadelScraper

SCRAPERS = {
    SiteType.WEBSDEPADEL: WebsdepadelScraper,
    SiteType.PLAYTOMIC: PlaytomicScraper,
    SiteType.MATCHPOINT: MatchpointScraper,
}
