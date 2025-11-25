from datetime import datetime
from typing import Any, Dict, Optional, TypeAlias

from pydantic import BaseModel, Field

from scapi import enums


Additional: TypeAlias = Dict[str, Any]


class ClientModel(BaseModel):
    pass


class RegionInfo(ClientModel):
    id: str
    name: str


class EmissionState(ClientModel):
    current_start: Optional[datetime] = Field(None, alias="currentStart")
    previous_start: Optional[datetime] = Field(None, alias="previousStart")
    previous_end: Optional[datetime] = Field(None, alias="previousEnd")


class ClanInfo(ClientModel):
    name: str
    uuid: str = Field(..., alias="id")
    tag: str
    level: int
    level_points: int = Field(..., alias="levelPoints")
    registration_time: datetime = Field(..., alias="registrationTime")
    alliance: Optional[enums.Alliance] = Field(None)
    description: str
    leader: str
    member_count: int = Field(..., alias="memberCount")


class ClanMember(ClientModel):
    name: str
    rank: enums.ClanRank
    join_time: datetime = Field(..., alias="joinTime")


class ClanAffiliation(ClientModel):
    info: ClanInfo
    member: ClanMember


class CharacterInfo(ClientModel):
    name: str
    uuid: str = Field(..., alias="id")
    creation_time: datetime = Field(..., alias="creationTime")


class Character(ClientModel):
    info: CharacterInfo = Field(..., alias="information")
    clan: Optional[ClanAffiliation] = Field(None)


class Statistic(ClientModel):
    id: str
    type: enums.StatType
    value: Any


class CharacterProfile(ClientModel):
    name: str = Field(..., alias="username")
    uuid: str
    status: str
    alliance: Optional[enums.Alliance] = Field(None)
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    displayed_achievements: list[str] = Field(..., alias="displayedAchievements")
    clan: Optional[ClanAffiliation] = Field(None)
    stats: list[Statistic]


class AuctionPrice(ClientModel):
    amount: int
    price: int
    time: datetime
    additional: Optional[Additional] = Field(None)


class AuctionLot(ClientModel):
    item_id: str = Field(..., alias="itemId")
    amount: int
    start_price: int = Field(..., alias="startPrice")
    current_price: Optional[int] = Field(None, alias="currentPrice")
    buyout_price: int = Field(..., alias="buyoutPrice")
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    additional: Optional[Additional] = Field(None)


class OperationParticipant(ClientModel):
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


class OperationSession(ClientModel):
    id: int
    map: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    difficulty: int
    duration_seconds: float = Field(..., alias="sessionDurationSeconds")
    reward: int = Field(..., alias="difficultyReward")
    participants: list[OperationParticipant]
