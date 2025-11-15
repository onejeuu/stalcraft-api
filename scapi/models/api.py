from datetime import datetime
from typing import Any, Dict, Optional, TypeAlias
from uuid import UUID
from pydantic import BaseModel, Field, field_validator

from scapi.enums import Alliance, Rank

Additional: TypeAlias = Dict[str, Any]


class RegionInfo(BaseModel):
    id: str
    name: str


class Emission(BaseModel):
    current_start: Optional[datetime] = Field(None, alias="currentStart")
    previous_start: Optional[datetime] = Field(None, alias="previousStart")
    previous_end: Optional[datetime] = Field(None, alias="previousEnd")


class ClanInfo(BaseModel):
    id: str
    name: str
    tag: str
    level: int
    level_points: int = Field(..., alias="levelPoints")
    registration_time: datetime = Field(..., alias="registrationTime")
    alliance: Optional[Alliance]
    description: str
    leader: str
    member_count: int = Field(..., alias="memberCount")


class ClanMember(BaseModel):
    name: str
    rank: Rank
    join_time: datetime = Field(..., alias="joinTime")


class CharacterClan(BaseModel):
    info: ClanInfo
    member: ClanMember


class CharacterInfo(BaseModel):
    id: str
    name: str
    creation_time: datetime = Field(..., alias="creationTime")


class Character(BaseModel):
    info: CharacterInfo = Field(..., alias="information")
    clan: Optional[CharacterClan] = Field(None)


class CharacterStatistic(BaseModel):
    id: str
    type: str
    value: Any


class CharacterProfile(BaseModel):
    username: str
    uuid: UUID
    status: str
    alliance: Alliance
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    displayed_achievements: list[str] = Field(..., alias="displayedAchievements")
    clan: Optional[CharacterClan] = Field(None)
    stats: list[CharacterStatistic]


class Price(BaseModel):
    amount: int
    price: int
    time: datetime
    additional: Optional[Additional]


class Lot(BaseModel):
    item_id: str = Field(..., alias="itemId")
    amount: int
    start_price: int = Field(..., alias="startPrice")
    current_price: Optional[int] = Field(None, alias="currentPrice")
    buyout_price: int = Field(..., alias="buyoutPrice")
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    additional: Optional[Additional]


class OperationParticipant(BaseModel):
    username: str
    death: int
    mob_kills: int = Field(..., alias="mobKills")
    damage_received: float = Field(..., alias="damageReceived")
    damage_dealt: float = Field(..., alias="damageDealt")
    armor_class: str = Field(..., alias="armorClass")
    armor_item_id: Optional[str] = Field(None, alias="armorItemId")
    armor_level: int = Field(..., alias="armorLevel")
    primary_weapon_item_id: Optional[str] = Field(None, alias="primaryWeaponItemId")
    primary_weapon_level: int = Field(..., alias="primaryWeaponLevel")
    secondary_weapon_item_id: Optional[str] = Field(None, alias="secondaryWeaponItemId")
    secondary_weapon_level: int = Field(..., alias="secondaryWeaponLevel")


class OperationSession(BaseModel):
    id: int
    map: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    difficulty: int
    duration_seconds: float = Field(..., alias="sessionDurationSeconds")
    reward: float = Field(..., alias="difficultyReward")
    participants: list[OperationParticipant]
