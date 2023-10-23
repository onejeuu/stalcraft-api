from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, validator


class TokenModel(BaseModel):
    token_type: str
    expires_in: datetime
    access_token: str

    @validator("expires_in", pre=True)
    def parse_expires_in(cls, expires_in: str):
        try:
            seconds = int(expires_in)
            return datetime.now() + timedelta(seconds=seconds)

        except Exception:
            return None


class AppToken(TokenModel):
    pass


class UserToken(TokenModel):
    refresh_token: str


class TokenInfo(BaseModel):
    id: int
    uuid: UUID
    login: str
    display_login: Optional[str]
    distributor: str
    distributor_id: Optional[str]
