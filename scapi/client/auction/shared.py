from scapi.client import models
from scapi.defaults import Default
from scapi.enums import Order, Region, SortAuction
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.http.types import Listing


class AuctionEndpoint(APIClient):
    """Endpoint for auction operations on specific item."""

    def __init__(
        self,
        *,
        http: HTTPClient,
        item_id: str,
        region: str | Region = Default.REGION,
        json: bool = Default.JSON,
    ):
        """
        Initialize auction endpoint.

        Args:
            http: HTTP client instance.
            item_id: Item identifier.
            region (optional): Game server region. Defaults to `RU`.
            json (optional): Return JSON instead of models. Defaults to `False`.
        """

        self._http = http
        self._item_id = item_id
        self._region = region
        self._json = json

    async def lots(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: str | SortAuction = Default.SORT_AUCTION,
        order: str | Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.AuctionLot]:
        """
        Retrieve active auction lots for item.

        Args:
            limit (optional): Amount of lots to return (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of lots to skip. Defaults to `0`.
            sort (optional): Sorting field. Defaults to `TIME_CREATED`.
            order (optional): Sorting direction. Defaults to `ASCENDING`.
            additional (optional): Include additional json data. Defaults to `False`.

        Returns:
            Paginated auction lots listing.
        """

        response = await self._http.GET(
            url=f"{self._region}/auction/{self._item_id}/lots",
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
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.AuctionPrice]:
        """
        Retrieve item price history.

        Args:
            limit (optional): Amount of prices to return (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of prices to skip. Defaults to `0`.
            additional (optional): Include additional json data. Defaults to `False`.

        Returns:
            Paginated price history listing.
        """

        response = await self._http.GET(
            url=f"{self._region}/auction/{self._item_id}/history",
            params=Params(
                limit=limit,
                offset=offset,
                additional=additional,
            ),
        )

        return self._parse(response, models.AuctionPrice, ("prices", "total"))

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id='{self._item_id}', region='{self._region}', http={self._http})"
