from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, validator


class RateLimit(BaseModel):
    limit: Optional[int] = Field(None, alias="x-ratelimit-limit")
    remaining: Optional[int] = Field(None, alias="x-ratelimit-remaining")
    reset: Optional[datetime] = Field(None, alias="x-ratelimit-reset")

    @validator("reset", pre=True)
    def parse_reset(cls, reset: str):
        try:
            ms = int(reset)
            timestamp = ms / 1000.0
            return datetime.fromtimestamp(timestamp)

        except Exception:
            return None
