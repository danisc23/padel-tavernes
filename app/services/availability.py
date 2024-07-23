import logging
from datetime import datetime, timedelta

import pytz
import requests
from bs4 import BeautifulSoup, Tag
from unidecode import unidecode

from app.cache import cache
from app.models import MatchFilter, MatchInfo, SiteInfo, SiteType
from app.services.common import get_weekly_dates

logging.basicConfig(level=logging.INFO, datefmt="%Y-%m-%d %H:%M:%S", format="%(asctime)s - %(levelname)s - %(message)s")

logger = logging.getLogger(__name__)


def check_filters(match_info: MatchInfo, match_filter: MatchFilter) -> bool:
    if match_filter.sport and unidecode(match_filter.sport.lower()) not in unidecode(match_info.sport.lower()):
        return False
    if match_filter.is_available is not None and match_info.is_available != match_filter.is_available:
        return False
    match_datetime = f"{match_info.date} {match_info.time}"
    if match_datetime < datetime.now().strftime("%Y-%m-%d %H:%M"):
        return False
    return True


def scrap_websdepadel_court_data(filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
    logging.info(f"Scraping {site.name} - {site.type}")
    data = []
    for date in get_weekly_dates(filter):
        date_data = []
        if cached_data := cache.get(f"{site.url}-{filter.sport}-{filter.is_available}-{date}"):
            data.extend(cached_data)
            continue

        url = f"https://www.{site.url}/partidas/{date}#contenedor-partidas"
        response = requests.get(url)
        soup = BeautifulSoup(response.text, "html.parser")

        availability = soup.find("div", id="resumen-disponibilidad")
        if not availability or not isinstance(availability, Tag):
            continue

        sports = availability.find_all("li", class_="deporte")
        for sport in sports:
            sport_name = sport.find("span", class_="nombre").get_text(strip=True)
            courts = sport.find_all("li", class_="pista")
            for court in courts:
                court_name = court.find("span", class_="nombre").get_text(strip=True)
                matchs = court.find_all("li", class_="partida")
                for match in matchs:
                    match_info = MatchInfo(
                        sport=sport_name,
                        court=court_name,
                        date=date,
                        time=match.find("a").get_text(strip=True),
                        url=match.find("a")["href"],
                        is_available="partida-reservada" not in match["class"],
                        site=site,
                    )
                    if check_filters(match_info, filter):
                        date_data.append(match_info)

        cache.set(f"{site.url}-{filter.sport}-{filter.is_available}-{date}", date_data, timeout=1800)
        data.extend(date_data)
    return data


def filter_playtomic_results(date: str, start_time: str, duration: int, used_start_times: set[str]) -> bool:
    # Filter to artificially reduce the amount of data
    match_date = datetime.strptime(f"{date} {start_time}", "%Y-%m-%d %H:%M:%S")
    if match_date < datetime.now():
        return False

    if duration != 90:
        return False

    if start_time in used_start_times:
        return False

    return True


def scrap_playtomic_court_data(filter: MatchFilter, site: SiteInfo) -> list[MatchInfo]:
    logging.info(f"Scraping {site.name} - {site.type}")
    data = []
    base_url = "https://playtomic.io/api/v1/availability"
    params = {
        "user_id": "me",
        "tenant_id": site.url.split("/")[-1],
        "sport_id": "PADEL",
    }
    court_friendly_name: dict[str, str] = {}
    for date in get_weekly_dates(filter):
        date_data = []
        if cached_data := cache.get(f"{site.url}-{filter.sport}-{filter.is_available}-{date}"):
            data.extend(cached_data)
            continue

        params["local_start_min"] = f"{date}T00:00:00"
        params["local_start_max"] = f"{date}T23:59:59"
        response = requests.get(base_url, params=params)
        if response.status_code != 200:
            logger.error(f"Error scraping {site.name} - {site.type.value}: {response.text}")
            continue

        for court in response.json():
            # Assign a friendly name to the court instead of the uuid
            if court["resource_id"] not in court_friendly_name:
                court_friendly_name[court["resource_id"]] = f"Padel {len(court_friendly_name) + 1}"

            used_start_times: set[str] = set()
            for slot in court["slots"]:
                if not filter_playtomic_results(date, slot["start_time"], slot["duration"], used_start_times):
                    continue

                time = datetime.strptime(slot["start_time"], "%H:%M:%S")
                used_start_times.add(slot["start_time"])
                used_start_times.add((time + timedelta(minutes=30)).strftime("%H:%M:%S"))
                used_start_times.add((time + timedelta(hours=1)).strftime("%H:%M:%S"))

                # time is +00:00, so we need to convert it to the local timezone
                time_utc = pytz.utc.localize(datetime.strptime(f"{date} {slot['start_time']}", "%Y-%m-%d %H:%M:%S"))
                time_str = time_utc.astimezone(pytz.timezone("Europe/Madrid")).strftime("%H:%M")

                match_info = MatchInfo(
                    sport="padel",
                    court=court_friendly_name[court["resource_id"]],
                    date=date,
                    time=time_str,
                    url=site.url,
                    is_available=True,
                    site=site,
                )
                if check_filters(match_info, filter):
                    date_data.append(match_info)

        cache.set(f"{site.url}-{filter.sport}-{filter.is_available}-{date}", date_data, timeout=1800)
        data.extend(date_data)

    return data


def get_court_data(filter: MatchFilter, sites: list[SiteInfo]) -> list[MatchInfo]:
    data: list[MatchInfo] = []
    for site in sites:
        match site.type:
            case SiteType.WEBSDEPADEL:
                data.extend(scrap_websdepadel_court_data(filter, site))
            case SiteType.PLAYTOMIC:
                data.extend(scrap_playtomic_court_data(filter, site))

    data.sort(key=lambda x: (x.date, x.time))
    return data
