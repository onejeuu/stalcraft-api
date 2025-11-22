from pathlib import Path

from .consts import BaseUrl
from .enums import Language, Order, Realm, Region, SortAuction, SortOperations


class Default:
    # Client
    BASE_URL = BaseUrl.PRODUCTION
    TIMEOUT = 60

    # Region
    REGION = Region.RU
    REALM = Realm.RU
    LANGUAGE = Language.RU

    # Api
    LIMIT = 20
    OFFSET = 0

    ORDER = Order.ASCENDING
    SORT_AUCTION = SortAuction.TIME_CREATED
    SORT_OPERATION = SortOperations.DATE_FINISH

    ADDITIONAL = False

    # OAuth
    REDIRECT_URI = "http://localhost"
    SCOPE = ""

    # Database
    DATABASE_PATH = Path.home() / "scapi" / "stalcraft.db"
