from enum import Enum


class BaseUrl(Enum):
    """
    DEMO: Demo API
    PRODUCTION: Production API
    """

    DEMO = "http://dapi.stalcraft.net"
    PRODUCTION = "http://eapi.stalcraft.net"


class Region(Enum):
    """
    RU: Russia
    EU: Europe
    NA: North America
    SEA: South East Asia
    """

    RU = "ru"
    EU = "eu"
    NA = "na"
    SEA = "sea"


class Sort(Enum):
    TIME_CREATED = "time_created"
    TIME_LEFT = "time_left"
    CURRENT_PRICE = "current_price"
    BUYOUT_PRICE = "buyout_price"


class Order(Enum):
    ASCENDING = "asc"
    DESCENDING = "desc"


class Rank(Enum):
    RECRUIT = "RECRUIT"
    COMMONER = "COMMONER"
    SOLDIER = "SOLDIER"
    SERGEANT = "SERGEANT"
    OFFICER = "OFFICER"
    COLONEL = "COLONEL"
    LEADER = "LEADER"
