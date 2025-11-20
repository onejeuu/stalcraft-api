from scapi import models
from scapi.defaults import Default
from scapi.enums import Order, Region, SortAuction
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.models.listing import Listing


class Auction:
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
    ) -> Listing[models.api.Price]:
        response = await self._http.GET(
            url=f"{self.region}/auction/{self.item_id}/history",
            params=Params(
                limit=limit,
                offset=offset,
                additional=additional,
            ),
        )

        return Listing(response, models.api.Price, "prices", "total")

    async def lots(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: SortAuction = Default.SORT_AUCTION,
        order: Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL,
    ) -> Listing[models.api.Lot]:
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

        return Listing(response, models.api.Lot, "lots", "total")
