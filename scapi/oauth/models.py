from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, field_validator


class OAuthModel(BaseModel):
    """Base model for OAuth response data."""

    pass


class TokenResponse(OAuthModel):
    """Base token response."""

    token_type: str
    access_token: str
    expires_in: datetime

    @field_validator("expires_in", mode="before")
    @classmethod
    def parse_expires_in(cls, expires_in: str):
        try:
            seconds = int(expires_in)
            return datetime.now() + timedelta(seconds=seconds)

        except Exception:
            return None


class AppToken(TokenResponse):
    """Application access token."""

    pass


class UserToken(TokenResponse):
    """User access and refresh token."""

    refresh_token: str


class UserInfo(OAuthModel):
    """User EXBO account information."""

    id: int
    uuid: UUID
    login: str
    display_login: Optional[str]
    distributor: str
    distributor_id: Optional[str]
