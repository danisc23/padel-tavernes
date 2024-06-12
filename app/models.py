import re

from pydantic import BaseModel, Field, field_validator


class MatchInfo(BaseModel):
    sport: str
    court: str
    date: str
    time: str
    url: str
    is_available: bool


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
