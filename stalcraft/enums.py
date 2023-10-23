from enum import StrEnum, auto


class Region(StrEnum):
    RU = RUSSIA = auto()
    EU = EUROPE = auto()
    NA = NORTH_AMERICA = auto()
    SEA = SOUTH_EAST_ASIA = auto()


class Sort(StrEnum):
    TIME_CREATED = auto()
    TIME_LEFT = auto()
    CURRENT_PRICE = auto()
    BUYOUT_PRICE = auto()


class Order(StrEnum):
    ASC = ASCENDING = auto()
    DESC = DESCENDING = auto()


class Rank(StrEnum):
    RECRUIT = auto()
    COMMONER = auto()
    SOLDIER = auto()
    SERGEANT = auto()
    OFFICER = auto()
    COLONEL = auto()
    LEADER = auto()
