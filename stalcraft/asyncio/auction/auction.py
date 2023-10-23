from typing import Any

from pydantic.types import NonNegativeInt

from stalcraft import Auction, Order, Region, Sort, schemas
from stalcraft.asyncio.api.base import AsyncBaseApi
from stalcraft.default import Default
from stalcraft.items import ItemId
from stalcraft.utils import Listing, Method, Params


class AsyncAuction(Auction):
    def __init__(
        self,
        api: AsyncBaseApi,
        item_id: ItemId,
        region: Region,
        json: bool
    ):
        super().__init__(api, item_id, region, json)
        self._api = api

    async def price_history(
        self,
        limit: NonNegativeInt = Default.LIMIT,
        offset: NonNegativeInt = Default.OFFSET,
        additional: bool = Default.ADDITIONAL
    ) -> Any | Listing[schemas.Price]:
        response = await self._api.request_get(
            Method(self.region, "auction", self.item_id, "history"),
            Params(offset=offset, limit=limit, additional=str(additional))
        )

        return response if self.json else Listing(response, schemas.Price, "prices", "total")

    async def lots(
        self,
        limit: NonNegativeInt = Default.LIMIT,
        offset: NonNegativeInt = Default.OFFSET,
        sort: Sort = Default.SORT,
        order: Order = Default.ORDER,
        additional: bool = Default.ADDITIONAL
    ) -> Any | Listing[schemas.Lot]:
        response = await self._api.request_get(
            Method(self.region, "auction", self.item_id, "lots"),
            Params(offset=offset, limit=limit, sort=sort, order=order, additional=str(additional))
        )

        return response if self.json else Listing(response, schemas.Lot, "lots", "total")
