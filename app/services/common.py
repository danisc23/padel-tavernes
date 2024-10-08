from datetime import datetime, timedelta

from unidecode import unidecode

from app.models import MatchFilter, MatchInfo


def get_weekly_dates(match_filter: MatchFilter, format: str = "%Y-%m-%d") -> list[str]:
    return [
        (datetime.now() + timedelta(days=day)).strftime(format) for day in sorted([int(d) for d in match_filter.days])
    ]


def check_filters(match_info: MatchInfo, match_filter: MatchFilter) -> bool:
    if match_filter.sport and unidecode(match_filter.sport.lower()) not in unidecode(match_info.sport.lower()):
        return False
    if match_filter.is_available is not None and match_info.is_available != match_filter.is_available:
        return False

    return True


def time_in_past(date: str, time: str) -> bool:
    match_datetime = datetime.strptime(f"{date} {time}", "%Y-%m-%d %H:%M")
    current_datetime = datetime.now()

    return match_datetime < current_datetime


def time_not_in_range(match_time: str, filter: MatchFilter) -> bool:
    dt_match_time = datetime.strptime(match_time, "%H:%M")
    dt_time_min = datetime.strptime(filter.time_min, "%H:%M")
    dt_time_max = datetime.strptime(filter.time_max, "%H:%M")
    return not (dt_time_min <= dt_match_time <= dt_time_max)
