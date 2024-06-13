from app.models import CourtUsage, Match, MatchFilter, SportUsage, UsageResponse
from app.services.availability import scrap_court_data


def get_court_usage(filter: MatchFilter, site: str) -> UsageResponse:
    court_data = scrap_court_data(filter, site)

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
