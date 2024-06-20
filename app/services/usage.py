from app.models import (
    CourtUsage,
    Match,
    MatchFilter,
    SiteInfo,
    SiteType,
    SportUsage,
    UsageResponse,
)
from app.services.availability import get_court_data


def get_court_usage(filter: MatchFilter, sites: list[SiteInfo]) -> UsageResponse:
    if len(sites) != 1:
        raise ValueError("Please provide only one site by using X-SITE header")

    if sites[0].type != SiteType.WEBSDEPADEL:
        raise ValueError(
            f"Site type {sites[0].type} is not supported for usage data. Currently only {SiteType.WEBSDEPADEL.value} is supported."
        )

    court_data = get_court_data(filter, sites)

    response = UsageResponse(sports=[])
    for match in court_data:
        sport = next((sport for sport in response.sports if sport.name == match.sport), None)
        if not sport:
            sport = SportUsage(name=match.sport, courts=[])
            response.sports.append(sport)

        court = next((court for court in sport.courts if court.name == match.court), None)
        if not court:
            court = CourtUsage(name=match.court, matches=[])
            sport.courts.append(court)

        court.matches.append(Match(date=match.date, time=match.time, is_available=match.is_available))

    return response
