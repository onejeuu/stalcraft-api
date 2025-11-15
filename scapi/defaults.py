from pathlib import Path

from .consts import BaseUrl
from .enums import Order, Realm, Region, SortAuction, SortOperation


class Default:
    BASE_URL = BaseUrl.PRODUCTION
    TIMEOUT = 30

    # Region
    REGION = Region.RU
    REALM = Realm.RU

    # Api
    LIMIT = 20
    OFFSET = 0

    ORDER = Order.ASCENDING
    SORT_AUCTION = SortAuction.TIME_CREATED
    SORT_OPERATION = SortOperation.DATE_FINISH

    ADDITIONAL = False

    # OAuth
    REDIRECT_URI = "http://localhost"
    RESPONSE_TYPE = "code"
    SCOPE = ""

    # Items
    ITEMS_DATABASE_PATH = Path.home() / "scapi" / "items.db"
