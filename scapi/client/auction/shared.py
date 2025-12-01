from scapi.client import models
from scapi.defaults import Default
from scapi.enums import Order, Region, SortAuction
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.http.types import Listing


class AuctionEndpoint(APIClient):
    def __init__(
        self,
        http: HTTPClient,
        item_id: str,
        region: str | Region = Default.REGION,
        json: bool = Default.JSON,
    ):
        self._http = http
        self._item_id = item_id
        self._region = region
        self._json = json

    async def price_history(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.AuctionPrice]:
        response = await self._http.GET(
            url=f"{self._region}/auction/{self._item_id}/history",
            params=Params(
                limit=limit,
                offset=offset,
                additional=additional,
            ),
        )

        return self._parse(response, models.AuctionPrice, ("prices", "total"))

    async def lots(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: str | SortAuction = Default.SORT_AUCTION,
        order: str | Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.AuctionLot]:
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

    def __repr__(self):
        return f"{self.__class__.__name__}(item_id='{self._item_id}', region='{self._region}', http={self._http})"
