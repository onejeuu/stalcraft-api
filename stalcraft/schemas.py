from dataclasses import dataclass
from datetime import datetime

from . import Rank


@dataclass
class RegionInfo:
    id: str
    name: str


@dataclass
class Emission:
    current_start: datetime
    previous_start: datetime
    previous_end: datetime


@dataclass
class ClanInfo:
    id: str
    name: str
    tag: str
    level: int
    level_points: int
    registration_time: datetime
    alliance: str
    description: str
    leader: str
    member_count: int


@dataclass
class Clans:
    total: int
    clans: list[ClanInfo]


@dataclass
class ClanMember:
    name: str
    rank: Rank
    join_time: datetime


@dataclass
class CharacterInfo:
    id: str
    name: str
    creation_time: datetime


@dataclass
class CharacterClan:
    info: ClanInfo
    member: ClanMember


@dataclass
class Character:
    info: CharacterInfo
    clan: CharacterClan


@dataclass
class Price:
    amount: int
    price: int
    time: datetime
    additional: dict


@dataclass
class Prices:
    total: int
    prices: list[Price]


@dataclass
class Lot:
    item_id: str
    start_price: int
    current_price: int
    buyout_price: int
    start_time: datetime
    end_time: datetime
    additional: dict


@dataclass
class Lots:
    total: int
    lots: list[Lot]
