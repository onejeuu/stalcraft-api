from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RateLimit(BaseModel):
    limit: Optional[int] = Field(None, alias="x-ratelimit-limit")
    remaining: Optional[int] = Field(None, alias="x-ratelimit-remaining")
    reset: Optional[datetime] = Field(None, alias="x-ratelimit-reset")

    @field_validator("reset", mode="before")
    @classmethod
    def parse_reset(cls, reset: str) -> Optional[datetime]:
        try:
            ms = int(reset)
            timestamp = ms / 1000.0
            return datetime.fromtimestamp(timestamp)

        except Exception:
            return None
