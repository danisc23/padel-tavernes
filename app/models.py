import re

from pydantic import BaseModel, Field, computed_field, field_validator


class SiteInfo(BaseModel):
    name: str
    url: str
    coordinates: tuple[float, float] | None = None


class AvailableSitesResponse(BaseModel):
    sites: list[SiteInfo]
    last_update: str


class MatchInfo(BaseModel):
    sport: str
    court: str
    date: str
    time: str
    url: str
    is_available: bool
    site: SiteInfo


class MatchFilter(BaseModel):
    sport: str | None = None
    is_available: bool | None = None
    days: str = "0123456"

    @field_validator("days", mode="before")
    @classmethod
    def validate_days(cls, value: str) -> str:
        if not re.match(r"^[0-6]*$", value):
            raise ValueError("days must be a string containing digits 0-6 only")
        if len(set(value)) != len(value):
            raise ValueError("days must have unique digits")
        int_days = sorted([int(d) for d in value])
        if not all(0 <= d <= 6 for d in int_days):
            raise ValueError("days must have digits between 0 and 6")
        return value


class GreedyPlayerInfo(BaseModel):
    name: str = ""
    count: int = 0
    dates: set[str] = Field(default_factory=set)
    hours: list[str] = Field(default_factory=list)

    @property
    def different_dates(self) -> int:
        return len(self.dates)


class GreedyPlayersFilter(BaseModel):
    sport: str = "padel"
    days: str = "0123456"

    @field_validator("sport", mode="before")
    @classmethod
    def validate_sport(cls, value: str) -> str:
        VALID_SPORTS = ["tenis", "tenis-dura", "padel", "futbol-sala", "fronton"]
        if value not in VALID_SPORTS:
            raise ValueError(f"sport must be one of {VALID_SPORTS}")
        return value

    @field_validator("days", mode="before")
    @classmethod
    def validate_days(cls, value: str) -> str:
        if not re.match(r"^[0-6]*$", value):
            raise ValueError("days must be a string containing digits 0-6 only")
        if len(set(value)) != len(value):
            raise ValueError("days must have unique digits")
        int_days = sorted([int(d) for d in value])
        if not all(0 <= d <= 6 for d in int_days):
            raise ValueError("days must have digits between 0 and 6")
        return value


class Match(BaseModel):
    date: str
    time: str
    is_available: bool


class UsageModel(BaseModel):
    @computed_field  # type: ignore[misc]
    @property
    def total_booked(self) -> int:
        raise NotImplementedError

    @computed_field  # type: ignore[misc]
    @property
    def total_available(self) -> int:
        raise NotImplementedError

    @computed_field  # type: ignore[misc]
    @property
    def total_matches(self) -> int:
        raise NotImplementedError

    @computed_field  # type: ignore[misc]
    @property
    def booked_percentage(self) -> float:
        return 100 if self.total_matches == 0 else round(self.total_booked / self.total_matches * 100, 2)


class CourtUsage(UsageModel):
    name: str
    matches: list[Match]

    @computed_field  # type: ignore[misc]
    @property
    def total_booked(self) -> int:
        return len([match for match in self.matches if not match.is_available])

    @computed_field  # type: ignore[misc]
    @property
    def total_available(self) -> int:
        return len([match for match in self.matches if match.is_available])

    @computed_field  # type: ignore[misc]
    @property
    def total_matches(self) -> int:
        return len(self.matches)


class SportUsage(UsageModel):
    name: str
    courts: list[CourtUsage]

    @computed_field  # type: ignore[misc]
    @property
    def total_booked(self) -> int:
        return sum(court.total_booked for court in self.courts)

    @computed_field  # type: ignore[misc]
    @property
    def total_available(self) -> int:
        return sum(court.total_available for court in self.courts)

    @computed_field  # type: ignore[misc]
    @property
    def total_matches(self) -> int:
        return sum(court.total_matches for court in self.courts)


class UsageResponse(UsageModel):
    sports: list[SportUsage]

    @computed_field  # type: ignore[misc]
    @property
    def total_booked(self) -> int:
        return sum(sport.total_booked for sport in self.sports)

    @computed_field  # type: ignore[misc]
    @property
    def total_available(self) -> int:
        return sum(sport.total_available for sport in self.sports)

    @computed_field  # type: ignore[misc]
    @property
    def total_matches(self) -> int:
        return sum(sport.total_matches for sport in self.sports)
