from enum import auto

from strenum import LowercaseStrEnum as StrEnum
from strenum import UppercaseStrEnum as UpStrEnum


class Region(StrEnum):
    RU = RUSSIA = auto()
    EU = EUROPE = auto()
    NA = NORTH_AMERICA = auto()
    SEA = SOUTH_EAST_ASIA = auto()


class Realm(StrEnum):
    RU = RUSSIA = auto()
    GLOBAL = auto()


class Language(StrEnum):
    RU = RUSSIAN = auto()
    EN = ENGLISH = auto()
    ES = SPANISH = auto()
    FR = FRENCH = auto()
    KO = KOREAN = auto()


class Alliance(StrEnum):
    STALKERS = auto()
    BANDITS = auto()
    DUTY = auto()
    FREEDOM = auto()
    MERC = auto()
    COVENANT = auto()


class Order(StrEnum):
    ASC = ASCENDING = auto()
    DESC = DESCENDING = auto()


class SortAuction(StrEnum):
    TIME_CREATED = auto()
    TIME_LEFT = auto()
    CURRENT_PRICE = auto()
    BUYOUT_PRICE = auto()


class SortOperations(StrEnum):
    DATE_FINISH = auto()
    DIFFICULTY = auto()


class ClanRank(UpStrEnum):
    RECRUIT = auto()
    COMMONER = auto()
    SOLDIER = auto()
    SERGEANT = auto()
    OFFICER = auto()
    COLONEL = auto()
    LEADER = auto()


class StatType(UpStrEnum):
    INTEGER = auto()
    DECIMAL = auto()
    DATE = auto()
    DURATION = auto()


class EntityType(StrEnum):
    LISTING = auto()
    STATS = auto()
    ACHIEVEMENTS = auto()
    SETTLEMENTS = auto()


class OperationsMap(StrEnum):
    BIG_CLEANUP = auto()
    SHOCK_THERAPY = auto()
