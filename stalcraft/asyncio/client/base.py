from abc import abstractmethod
from pathlib import Path
from typing import Any

from httpx import QueryParams

from stalcraft import Region, schemas
from stalcraft.asyncio.api.base import AsyncBaseApi
from stalcraft.asyncio.auction import AsyncAuction
from stalcraft.client.base import BaseClient
from stalcraft.defaults import Default
from stalcraft.items import ItemId
from stalcraft.utils import Listing


class AsyncBaseClient(BaseClient):
    def __init__(
        self,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        self.base_url = base_url
        self.json = json

        self._api = self._get_api()

    @abstractmethod
    def _get_api(self) -> AsyncBaseApi:
        ...

    async def regions(self) -> Any | list[schemas.RegionInfo]:
        response = await self._api.request_get(
            Path("regions")
        )

        return response if self.json else [schemas.RegionInfo.model_validate(region) for region in response]

    def auction(
        self,
        item_id: ItemId,
        region: Region = Default.REGION
    ) -> AsyncAuction:
        return AsyncAuction(self._api, item_id, region, self.json)

    async def emission(
        self,
        region: Region = Default.REGION
    ) -> Any | schemas.Emission:
        response = await self._api.request_get(
            Path(region, "emission")
        )

        return response if self.json else schemas.Emission.model_validate(response)

    async def character_profile(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | schemas.CharacterProfile:
        response = await self._api.request_get(
            Path(region, "character", "by-name", character, "profile")
        )

        return response if self.json else schemas.CharacterProfile.model_validate(response)

    async def clans(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        region: Region = Default.REGION
    ) -> Any | Listing[schemas.ClanInfo]:
        response = await self._api.request_get(
            Path(region, "clans"),
            QueryParams(limit=limit, offset=offset)
        )

        return response if self.json else Listing(response, schemas.ClanInfo, "data", "totalClans")
