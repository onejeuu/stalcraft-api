from pathlib import Path
from typing import Any

from httpx import QueryParams

from stalcraft import Order, Region, Sort, schemas
from stalcraft.api.base import BaseApi
from stalcraft.defaults import Default
from stalcraft.items import ItemId
from stalcraft.utils import Listing


class Auction:
    def __init__(
        self,
        api: BaseApi,
        item_id: ItemId,
        region: Region,
        json: bool
    ):
        self._api = api
        self.item_id = str(item_id)
        self.region = region
        self.json = json

    def price_history(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        additional: bool = Default.ADDITIONAL
    ) -> Any | Listing[schemas.Price]:
        """
        Returns history of prices for lots which were bought from auction for the given item.
        Prices are sorted in descending order by recorded time of purchase.

        Args:
            limit: Amount of clans to return, starting from offset, (0-100). Defaults to 20.
            offset: Amount of clans in list to skip. Defaults to 0.
            additional: Whether to include additional information (dict) about lots. Defaults to False.
        """

        response = self._api.request_get(
            Path(self.region, "auction", self.item_id, "history"),
            QueryParams(limit=limit, offset=offset, additional=additional)
        )

        return response if self.json else Listing(response, schemas.Price, "prices", "total")

    def lots(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: Sort = Default.SORT,
        order: Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL
    ) -> Any | Listing[schemas.Lot]:
        """
        Returns list of currently active lots on the auction for the given item.
        Lots are sorted based on given parameter.

        Args:
            limit: Amount of clans to return, starting from offset, (0-100). Defaults to 20.
            offset: Amount of clans in list to skip. Defaults to 0.
            sort: Property to sort by. Defaults to TIME_CREATED.
            order: Either asc or desc. Defaults to ASCENDING.
            additional: Whether to include additional information (dict) about lots. Defaults to False.
        """

        response = self._api.request_get(
            Path(self.region, "auction", self.item_id, "lots"),
            QueryParams(limit=limit, offset=offset, sort=sort, order=order, additional=additional)
        )

        return response if self.json else Listing(response, schemas.Lot, "lots", "total")

    def __str__(self):
        return f"<{self.__class__.__name__}> item_id='{self.item_id}' region='{self.region}'"
