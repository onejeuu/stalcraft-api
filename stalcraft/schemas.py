from uuid import UUID
from typing import Optional, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime, timedelta

from . import Rank


class DateTimeValidator:
    @classmethod
    def parse(cls, value):
        try:
            return datetime.fromisoformat(value)
        except Exception:
            return None

    @classmethod
    def expires_in(cls, value):
        expires_time = datetime.now() + timedelta(seconds=value)
        return expires_time


class RegionInfo(BaseModel):
    """RegionInfo"""

    id: str
    name: str


class Emission(BaseModel):
    """EmissionResponse"""

    current_start: Optional[datetime] = Field(None, alias="currentStart")
    previous_start: datetime = Field(..., alias="previousStart")
    previous_end: datetime = Field(..., alias="previousEnd")

    @validator("current_start", "previous_start", "previous_end", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class ClanInfo(BaseModel):
    """ClanInfo"""

    id: str
    name: str
    tag: str
    level: int
    level_points: int = Field(..., alias="levelPoints")
    registration_time: datetime = Field(..., alias="registrationTime")
    alliance: str
    description: str
    leader: str
    member_count: int = Field(..., alias="memberCount")

    @validator("registration_time", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class ClanMember(BaseModel):
    """ClanMember"""

    name: str
    rank: Rank
    join_time: datetime = Field(..., alias="joinTime")

    @validator("rank", pre=True)
    def parse_rank(cls, value):
        return Rank[value]

    @validator("join_time", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class CharacterClanInfo(BaseModel):
    """CharacterClanInfo"""

    info: ClanInfo
    member: ClanMember


class CharacterInfo(BaseModel):
    """CharacterMetaInfo"""

    id: str
    name: str
    creation_time: datetime = Field(..., alias="creationTime")

    @validator("creation_time", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class CharacterClan(BaseModel):
    """FullCharacterInfo"""

    info: CharacterInfo = Field(..., alias="information")
    clan: Optional[CharacterClanInfo] = Field(None)


class CharacterStatistic(BaseModel):
    """CharacterStatValue"""

    id: str
    type: str
    value: Any


class CharacterProfile(BaseModel):
    """CharacterProfileData"""

    username: str
    uuid: UUID
    status: str
    alliance: str
    last_login: Optional[datetime] = Field(..., alias="lastLogin")
    displayed_achievements: list[str] = Field(..., alias="displayedAchievements")
    clan: Optional[CharacterClanInfo] = Field(None)
    stats: list[CharacterStatistic]

    @validator("last_login", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class Price(BaseModel):
    """PriceEntry"""

    amount: int
    price: int
    time: datetime
    additional: Optional[dict]

    @validator("time", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class Lot(BaseModel):
    """Lot"""

    item_id: str = Field(..., alias="itemId")
    amount: int
    start_price: int = Field(..., alias="startPrice")
    current_price: Optional[int] = Field(None, alias="currentPrice")
    buyout_price: int = Field(..., alias="buyoutPrice")
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    additional: Optional[dict]

    @validator("start_time", "end_time", pre=True)
    def parse_datetime(cls, value):
        return DateTimeValidator.parse(value)


class TokenModel(BaseModel):
    token_type: str
    expires_in: datetime
    access_token: str

    @validator("expires_in", pre=True)
    def parse_expires_in(cls, value):
        return DateTimeValidator.expires_in(value)


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
