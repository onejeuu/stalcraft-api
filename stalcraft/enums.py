from enum import Enum


class BaseUrl(Enum):
    """
    DEMO: Demo API
    PRODUCTION: Production API
    """

    DEMO = "http://dapi.stalcraft.net"
    PRODUCTION = "http://eapi.stalcraft.net"


class StatusCode(Enum):
    OK = 200
    INVALID_PARAMETER = 400
    UNAUTHORISED = 401
    NOT_FOUND = 404
    RATE_LIMIT = 429


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
    ASCENDING = ASC = "asc"
    DESCENDING = DESC = "desc"


class Rank(Enum):
    RECRUIT = "RECRUIT"
    COMMONER = "COMMONER"
    SOLDIER = "SOLDIER"
    SERGEANT = "SERGEANT"
    OFFICER = "OFFICER"
    COLONEL = "COLONEL"
    LEADER = "LEADER"
