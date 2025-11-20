from enum import auto

from strenum import LowercaseStrEnum as StrEnum
from strenum import UppercaseStrEnum as UpStrEnum


class Region(StrEnum):
    RU = RUSSIA = auto()
    EU = EUROPE = auto()
    NA = NORTH_AMERICA = auto()
    SEA = SOUTH_EAST_ASIA = auto()


class Realm(StrEnum):
    RU = auto()
    GLOBAL = EU = NA = SEA = auto()


class Language(StrEnum):
    RU = RUSSIAN = auto()
    EN = ENGLISH = auto()
    ES = SPANISH = auto()
    FR = FRENCH = auto()


class Order(StrEnum):
    ASC = ASCENDING = auto()
    DESC = DESCENDING = auto()


class SortAuction(StrEnum):
    TIME_CREATED = auto()
    TIME_LEFT = auto()
    CURRENT_PRICE = auto()
    BUYOUT_PRICE = auto()


class SortOperation(StrEnum):
    DATE_FINISH = auto()
    DIFFICULTY = auto()


class Alliance(StrEnum):
    STALKERS = auto()
    BANDITS = auto()
    DUTY = auto()
    FREEDOM = auto()
    MERC = auto()
    COVENANT = auto()


class Rank(UpStrEnum):
    RECRUIT = auto()
    COMMONER = auto()
    SOLDIER = auto()
    SERGEANT = auto()
    OFFICER = auto()
    COLONEL = auto()
    LEADER = auto()


class EntityType(StrEnum):
    LISTING = auto()
    STATS = auto()
    ACHIEVEMENTS = auto()
    SETTLEMENTS = auto()
