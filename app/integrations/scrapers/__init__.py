from app.models import SiteType

from .playtomic_scraper import PlaytomicScraper
from .websdepadel_scraper import WebsdepadelScraper

SCRAPERS = {
    SiteType.WEBSDEPADEL: WebsdepadelScraper,
    SiteType.PLAYTOMIC: PlaytomicScraper,
}
