from typing import ClassVar

from .enums import Language, Order, Realm, Region, SortAuction, SortOperations


class Config:
    """Global configuration settings."""

    REGION: ClassVar[str | Region] = Region.RU
    """Game server region. Defaults to `RU`."""

    REALM: ClassVar[str | Realm] = Realm.RU
    """Game version realm. Defaults to `RU`."""

    LANGUAGE: ClassVar[str | Language] = Language.RU
    """**UNUSED**. Entity localization. Defaults to `RU`."""

    LIMIT: ClassVar[int] = 20
    """Pagination limit (`0`-`100`). Defaults to `20`."""

    OFFSET: ClassVar[int] = 0
    """Pagination offset. Defaults to `0`."""

    ORDER: ClassVar[str | Order] = Order.ASCENDING
    """Result ordering direction. Defaults to `ASCENDING`."""

    SORT_AUCTION: ClassVar[str | SortAuction] = SortAuction.TIME_CREATED
    """Auction sorting field. Defaults to `TIME_CREATED`."""

    SORT_OPERATION: ClassVar[str | SortOperations] = SortOperations.DATE_FINISH
    """Operations sessions sorting field. Defaults to `DATE_FINISH`."""

    ADDITIONAL: ClassVar[bool] = False
    """Auction additional json data flag. Defaults to `False`."""
