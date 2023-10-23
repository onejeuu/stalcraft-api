from typing import NamedTuple

from stalcraft.consts import BaseUrl, ItemFolder
from stalcraft.enums import Order, Region, Sort


class Default(NamedTuple):
    # ? Api
    BASE_URL = BaseUrl.PRODUCTION
    REGION = Region.RU
    JSON = False

    # ? Requests
    LIMIT = 20
    OFFSET = 0
    SORT = Sort.TIME_CREATED
    ORDER = Order.ASCENDING
    ADDITIONAL = False

    # ? Auth
    REDIRECT_URI = "http://localhost"
    RESPONSE_TYPE = "code"
    SCOPE = ""

    # ? Some requests in auction can take a LARGE amount of time.
    TIMEOUT_SECONDS = 60.0

    # ? Items Ids
    ITEMS_FOLDER = ItemFolder.RU
