from enum import Enum


class ApiLink(Enum):
    """
    DEMO: Демонстрационный API
    PRODUCTION: Полноценный API
    """

    DEMO = "http://dapi.stalcraft.net"
    PRODUCTION = "http://eapi.stalcraft.net"


class Region(Enum):
    """
    RU: Russia / Россия
    EU: Europe / Европа
    NA: North America / Северная Америка
    SEA: South East Asia / Юго-Восточная Азия
    """
    RU = 'ru'
    EU = 'eu'
    NA = 'na'
    SEA = 'sea'


class Sort(Enum):
    """
    TIME_CREATED: Время создания
    TIME_LEFT: Времени осталось
    CURRENT_PRICE: Цена ставки
    BUYOUT_PRICE: Цена выкупа
    """

    TIME_CREATED = "time_created"
    TIME_LEFT = "time_left"
    CURRENT_PRICE = "current_price"
    BUYOUT_PRICE = "buyout_price"


class Order(Enum):
    """
    ASCENDING: Возростание
    DESCENDING: Убывание
    """

    ASCENDING = "asc"
    DESCENDING = "desc"
