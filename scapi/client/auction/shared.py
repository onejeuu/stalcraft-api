from scapi.client import models
from scapi.client.types import Listing
from scapi.defaults import Default
from scapi.enums import Order, Region, SortAuction
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params


class AuctionEndpoint(APIClient):
    def __init__(
        self,
        http: HTTPClient,
        item_id: str,
        region: Region = Default.REGION,
    ):
        self._http = http
        self.item_id = item_id
        self.region = region

    async def price_history(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.Price]:
        response = await self._http.GET(
            url=f"{self.region}/auction/{self.item_id}/history",
            params=Params(
                limit=limit,
                offset=offset,
                additional=additional,
            ),
        )

        return Listing(response, models.Price, "prices", "total")

    async def lots(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: SortAuction = Default.SORT_AUCTION,
        order: Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.Lot]:
        response = await self._http.GET(
            url=f"{self.region}/auction/{self.item_id}/lots",
            params=Params(
                limit=limit,
                offset=offset,
                sort=sort,
                order=order,
                additional=additional,
            ),
        )

        return Listing(response, models.Lot, "lots", "total")

    def __str__(self):
        return f"<{self.__class__.__name__} item_id='{self.item_id}' region='{self.region}' http={self._http}>"
