from datetime import datetime, timedelta

from unidecode import unidecode

from app.models import MatchFilter, MatchInfo


def get_weekly_dates(match_filter: MatchFilter) -> list[str]:
    return [
        (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        for day in sorted([int(d) for d in match_filter.days])
    ]


def check_filters(match_info: MatchInfo, match_filter: MatchFilter) -> bool:
    if match_filter.sport and unidecode(match_filter.sport.lower()) not in unidecode(match_info.sport.lower()):
        return False
    if match_filter.is_available is not None and match_info.is_available != match_filter.is_available:
        return False
    match_datetime = f"{match_info.date} {match_info.time}"
    if match_datetime < datetime.now().strftime("%Y-%m-%d %H:%M"):
        return False
    return True


def time_not_in_range(match_time: str, time_min: str, time_max: str) -> bool:
    dt_match_time = datetime.strptime(match_time, "%H:%M")
    dt_time_min = datetime.strptime(time_min, "%H:%M")
    dt_time_max = datetime.strptime(time_max, "%H:%M")
    return not (dt_time_min <= dt_match_time <= dt_time_max)
