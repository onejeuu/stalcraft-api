from .consts import BaseUrl
from .enums import Language, Order, Realm, Region, SortAuction, SortOperations


class Default:
    """Default values for parameters."""

    # Client
    BASE_URL = BaseUrl.PRODUCTION
    TIMEOUT = 60
    JSON = False

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
