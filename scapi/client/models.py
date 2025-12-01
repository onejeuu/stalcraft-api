from datetime import datetime
from typing import Any, Dict, Optional, TypeAlias

from pydantic import BaseModel, Field

from scapi import enums


Additional: TypeAlias = Dict[str, Any]


class ClientModel(BaseModel):
    """Base model for API response."""

    pass


class RegionInfo(ClientModel):
    """
    Game server region information.

    Endpoint: https://eapi.stalcraft.net/reference#/paths/regions/get
    """

    id: str
    name: str


class EmissionState(ClientModel):
    """
    Current and previous emission status.

    Reference: https://eapi.stalcraft.net/reference#/schemas/EmissionResponse
    """

    current_start: Optional[datetime] = Field(None, alias="currentStart")
    previous_start: Optional[datetime] = Field(None, alias="previousStart")
    previous_end: Optional[datetime] = Field(None, alias="previousEnd")


class ClanInfo(ClientModel):
    """
    Clan details and statistics.

    Reference: https://eapi.stalcraft.net/reference#/schemas/ClanInfo
    """

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
    """
    Clan member details.

    Reference: https://eapi.stalcraft.net/reference#/schemas/ClanMember
    """

    name: str
    rank: enums.ClanRank
    join_time: datetime = Field(..., alias="joinTime")


class ClanAffiliation(ClientModel):
    """
    Character clan affiliation.

    Reference: https://eapi.stalcraft.net/reference#/schemas/CharacterClanInfo
    """

    info: ClanInfo
    member: ClanMember


class CharacterInfo(ClientModel):
    """Basic character metadata."""

    name: str
    uuid: str = Field(..., alias="id")
    creation_time: datetime = Field(..., alias="creationTime")


class Character(ClientModel):
    """
    User Character details.

    Endpoint: https://eapi.stalcraft.net/reference#/paths/region--characters/get
    """

    info: CharacterInfo = Field(..., alias="information")
    clan: Optional[ClanAffiliation] = Field(None)


class Statistic(ClientModel):
    """
    Character statistic.

    Reference: https://eapi.stalcraft.net/reference#/schemas/CharacterStatValue
    """

    id: str
    type: enums.StatType
    value: Any


class CharacterProfile(ClientModel):
    """
    Public character profile.

    Reference: https://eapi.stalcraft.net/reference#/schemas/CharacterProfileData
    """

    name: str = Field(..., alias="username")
    uuid: str
    status: str
    alliance: Optional[enums.Alliance] = Field(None)
    last_login: Optional[datetime] = Field(None, alias="lastLogin")
    displayed_achievements: list[str] = Field(..., alias="displayedAchievements")
    clan: Optional[ClanAffiliation] = Field(None)
    stats: list[Statistic]


class AuctionLot(ClientModel):
    """
    Actual auction item lot.

    Reference: https://eapi.stalcraft.net/reference#/schemas/Lot
    """

    item_id: str = Field(..., alias="itemId")
    amount: int
    start_price: int = Field(..., alias="startPrice")
    current_price: Optional[int] = Field(None, alias="currentPrice")
    buyout_price: int = Field(..., alias="buyoutPrice")
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    additional: Optional[Additional] = Field(None)


class AuctionPrice(ClientModel):
    """
    Historical auction price entry.

    Reference: https://eapi.stalcraft.net/reference#/schemas/PriceEntry
    """

    amount: int
    price: int
    time: datetime
    additional: Optional[Additional] = Field(None)


class OperationParticipant(ClientModel):
    """
    Player statistics in an operation session.

    Reference: https://eapi.stalcraft.net/reference#/schemas/OperationSessionParticipant
    """

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
    """
    Operation session details.

    Reference: https://eapi.stalcraft.net/reference#/schemas/OperationSession
    """

    id: int
    map: str
    start_time: datetime = Field(..., alias="startTime")
    end_time: datetime = Field(..., alias="endTime")
    difficulty: int
    duration_seconds: float = Field(..., alias="sessionDurationSeconds")
    reward: int = Field(..., alias="difficultyReward")
    participants: list[OperationParticipant]
