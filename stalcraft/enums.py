from enum import StrEnum, auto


class Region(StrEnum):
    RU = RUSSIA = auto()
    EU = EUROPE = auto()
    NA = NORTH_AMERICA = auto()
    SEA = SOUTH_EAST_ASIA = auto()


class AuctionSort(StrEnum):
    TIME_CREATED = auto()
    TIME_LEFT = auto()
    CURRENT_PRICE = auto()
    BUYOUT_PRICE = auto()


Sort = AuctionSort


class OperationSort(StrEnum):
    DATE_FINISH = auto()
    DIFFICULTY = auto()


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


class ItemsFolder(StrEnum):
    RU = auto()
    GLOBAL = EU = NA = SEA = auto()
