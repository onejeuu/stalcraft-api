from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class RateLimit(BaseModel):
    limit: Optional[int] = Field(None, alias="x-ratelimit-limit")
    remaining: Optional[int] = Field(None, alias="x-ratelimit-remaining")
    used: Optional[int] = Field(None, alias="x-ratelimit-used")
    reset: Optional[datetime] = Field(None, alias="x-ratelimit-reset")

    @property
    def estimated_used(self) -> Optional[int]:
        if self.limit is not None and self.remaining is not None:
            return max(0, self.limit - self.remaining)
        return None

    @field_validator("reset", mode="before")
    @classmethod
    def parse_reset(cls, reset: str) -> Optional[datetime]:
        try:
            timestamp = int(reset)
            power = len(reset) - 10
            divisor = 10 ** max(0, power)
            return datetime.fromtimestamp(int(timestamp / divisor))

        except Exception:
            return None
