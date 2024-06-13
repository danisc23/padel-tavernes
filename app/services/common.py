from datetime import datetime, timedelta

from app.models import GreedyPlayersFilter, MatchFilter


def get_weekly_dates(match_filter: MatchFilter | GreedyPlayersFilter) -> list[str]:
    return [
        (datetime.now() + timedelta(days=day)).strftime("%Y-%m-%d")
        for day in sorted([int(d) for d in match_filter.days])
    ]
