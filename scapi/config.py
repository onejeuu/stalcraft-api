from typing import ClassVar

from .enums import Language, Order, Realm, Region, SortAuction, SortOperations


class Config:
    """Global configuration settings."""

    REGION: ClassVar[str | Region] = Region.RU
    """Game server region. Defaults to `ru`."""

    REALM: ClassVar[str | Realm] = Realm.RU
    """Game version realm. Defaults to `ru`."""

    LANGUAGE: ClassVar[str | Language] = Language.RU
    """**UNUSED**. Entity localization. Defaults to `ru`."""

    LIMIT: ClassVar[int] = 20
    """Pagination limit (`0`-`100`). Defaults to `20`."""

    OFFSET: ClassVar[int] = 0
    """Pagination offset. Defaults to `0`."""

    ORDER_AUCTION: ClassVar[str | Order] = Order.DESCENDING
    """Auction ordering direction. Defaults to `descending`."""

    ORDER_OPERATION: ClassVar[str | Order] = Order.DESCENDING
    """Operations ordering direction. Defaults to `descending`."""

    SORT_AUCTION: ClassVar[str | SortAuction] = SortAuction.TIME_CREATED
    """Auction sorting field. Defaults to `time_created`."""

    SORT_OPERATION: ClassVar[str | SortOperations] = SortOperations.DATE_FINISH
    """Operations sessions sorting field. Defaults to `date_finish`."""

    ADDITIONAL: ClassVar[bool] = False
    """Auction additional json data flag. Defaults to `False`."""
