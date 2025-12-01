from enum import auto

from strenum import LowercaseStrEnum as StrEnum
from strenum import UppercaseStrEnum as UpStrEnum


class Region(StrEnum):
    """Game server region for STALCRAFT API requests."""

    RU = RUSSIA = auto()
    EU = EUROPE = auto()
    NA = NORTH_AMERICA = auto()
    SEA = SOUTH_EAST_ASIA = auto()


class Realm(StrEnum):
    """Game version with separate database."""

    RU = RUSSIA = auto()
    GLOBAL = auto()


class Language(StrEnum):
    """Supported localization languages."""

    RU = RUSSIAN = auto()
    EN = ENGLISH = auto()
    ES = SPANISH = auto()
    FR = FRENCH = auto()
    KO = KOREAN = auto()


class Alliance(StrEnum):
    """Game alliance name."""

    STALKERS = auto()
    BANDITS = auto()
    DUTY = auto()
    FREEDOM = auto()
    MERC = auto()
    COVENANT = auto()


class ClanRank(UpStrEnum):
    """Game clan member rank name."""

    RECRUIT = auto()
    COMMONER = auto()
    SOLDIER = auto()
    SERGEANT = auto()
    OFFICER = auto()
    COLONEL = auto()
    LEADER = auto()


class Order(StrEnum):
    """Results ordering direction."""

    ASC = ASCENDING = auto()
    DESC = DESCENDING = auto()


class SortAuction(StrEnum):
    """Auction results sorting criteria."""

    TIME_CREATED = auto()
    TIME_LEFT = auto()
    CURRENT_PRICE = auto()
    BUYOUT_PRICE = auto()


class SortOperations(StrEnum):
    """Operations session sorting criteria."""

    DATE_FINISH = auto()
    DIFFICULTY = auto()


class OperationsMap(StrEnum):
    """Operations session map names."""

    BIG_CLEANUP = auto()
    SHOCK_THERAPY = auto()


class StatType(UpStrEnum):
    """Statistic value type."""

    INTEGER = auto()
    DECIMAL = auto()
    DATE = auto()
    DURATION = auto()
