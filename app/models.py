import re
from datetime import datetime, timedelta
from enum import Enum
from typing import Self

from pydantic import BaseModel, Field, computed_field, field_validator, model_validator


class SiteType(str, Enum):
    WEBSDEPADEL = "websdepadel"
    MATCHPOINT = "matchpoint"
    PLAYTOMIC = "playtomic"


class SiteInfo(BaseModel):
    name: str
    url: str
    type: SiteType
    coordinates: tuple[float, float] | None = None

    class Config:
        use_enum_values = True


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


class GeolocationFilter(BaseModel):
    latitude: float
    longitude: float
    radius_km: int

    @field_validator("latitude", mode="before")
    @classmethod
    def validate_latitude(cls, value: float) -> float:
        if not -90 <= value <= 90:
            raise ValueError("latitude must be between -90 and 90")
        return value

    @field_validator("longitude", mode="before")
    @classmethod
    def validate_longitude(cls, value: float) -> float:
        if not -180 <= value <= 180:
            raise ValueError("longitude must be between -180 and 180")
        return value

    @field_validator("radius_km", mode="before")
    @classmethod
    def validate_radius_km(cls, value: int) -> float:
        if value <= 0:
            raise ValueError("radius_km must be greater than 0")
        return value


class MatchFilter(BaseModel):
    sport: str | None = None
    is_available: bool | None = None
    days: str
    time_min: str
    time_max: str

    @field_validator("days", mode="before")
    @classmethod
    def validate_days(cls, value: str) -> str:
        if not (1 <= len(value) <= 3):
            raise ValueError("days must be a string containing 1 to 3 digits")
        if len(set(value)) != len(value):
            raise ValueError("days must have unique digits")
        int_days = sorted([int(d) for d in value])
        if not all(0 <= d <= 6 for d in int_days):
            raise ValueError("days must have digits between 0 and 6")
        if not all(b - a == 1 for a, b in zip(int_days, int_days[1:])):
            raise ValueError("days must be consecutive")

        return value

    @field_validator("time_min", mode="before")
    @classmethod
    def validate_time_min(cls, value: str) -> str:
        if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", value):
            raise ValueError("time_min must be a string in the format HH:MM")
        return value

    @field_validator("time_max", mode="before")
    @classmethod
    def validate_time_max(cls, value: str) -> str:
        if not re.match(r"^(?:[01]\d|2[0-3]):[0-5]\d$", value):
            raise ValueError("time_max must be a string in the format HH:MM")
        return value

    @model_validator(mode="after")
    def check_time_difference(self) -> Self:
        time_min = self.time_min
        time_max = self.time_max
        if time_min and time_max:
            time_min_dt = datetime.strptime(time_min, "%H:%M")
            time_max_dt = datetime.strptime(time_max, "%H:%M")
            if time_max_dt - time_min_dt > timedelta(hours=3):
                raise ValueError("The difference between time_min and time_max must not exceed 3 hours")
            if time_max_dt < time_min_dt:
                raise ValueError("time_max must be greater than time_min")
        return self


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
