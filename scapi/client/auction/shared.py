from typing import Optional

from scapi.client import models
from scapi.config import Config
from scapi.consts import Defaults
from scapi.enums import Order, Region, SortAuction
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.http.types import Listing


class AuctionEndpoint(APIClient):
    """Auction endpoint for specified item."""

    def __init__(
        self,
        *,
        http: HTTPClient,
        item_id: str,
        json: bool = Defaults.JSON,
        region: Optional[Region | str] = None,
    ):
        """
        Initialize auction endpoint.

        Args:
            http: HTTP client instance.
            item_id: Item identifier.
            json (optional): Return JSON instead of models. Defaults to `False`.
            region (optional): Default game server region. Defaults to `ru`.
        """

        self._http = http
        self._item_id = item_id
        self._json = json
        self._region = region

    async def lots(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[SortAuction | str] = None,
        order: Optional[Order | str] = None,
        additional: Optional[bool] = None,
        region: Optional[Region | str] = None,
    ) -> Listing[models.AuctionLot]:
        """
        Retrieve active auction lots for item.

        Args:
            limit (optional): Amount of lots to return (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of lots to skip. Defaults to `0`.
            sort (optional): Sorting field. Defaults to `time_created`.
            order (optional): Sorting direction. Defaults to `descending`.
            additional (optional): Include additional json data. Defaults to `False`.
            region (optional): Default game server region. Defaults to `ru`.

        Returns:
            Paginated auction lots listing.
        """

        limit = max(0, min(200, limit or Config.LIMIT))
        offset = max(0, offset or Config.OFFSET)
        sort = (sort or Config.SORT_AUCTION).lower()
        order = (order or Config.ORDER_AUCTION).lower()
        additional = bool(additional or Config.ADDITIONAL)
        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/auction/{self._item_id}/lots",
            params=Params(
                limit=limit,
                offset=offset,
                sort=sort,
                order=order,
                additional=additional,
            ),
        )

        return self._parse(response, models.AuctionLot, ("lots", "total"))

    async def price_history(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        additional: Optional[bool] = None,
        region: Optional[Region | str] = None,
    ) -> Listing[models.AuctionPrice]:
        """
        Retrieve item price history.

        Args:
            limit (optional): Amount of prices to return (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of prices to skip. Defaults to `0`.
            additional (optional): Include additional json data. Defaults to `False`.
            region (optional): Default game server region. Defaults to `ru`.

        Returns:
            Paginated price history listing.
        """

        limit = max(0, min(200, limit or Config.LIMIT))
        offset = max(0, offset or Config.OFFSET)
        additional = bool(additional or Config.ADDITIONAL)
        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/auction/{self._item_id}/history",
            params=Params(
                limit=limit,
                offset=offset,
                additional=additional,
            ),
        )

        return self._parse(response, models.AuctionPrice, ("prices", "total"))

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id='{self._item_id}', http={self._http})"
