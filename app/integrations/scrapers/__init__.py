from app.models import SiteType

from .playtomic_scraper import PlaytomicScrapper
from .websdepadel_scraper import WebsdepadelScrapper

SCRAPPERS = {
    SiteType.WEBSDEPADEL: WebsdepadelScrapper,
    SiteType.PLAYTOMIC: PlaytomicScrapper,
}
