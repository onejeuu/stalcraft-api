from abc import abstractmethod
from typing import Any

from stalcraft import Region, schemas
from stalcraft.asyncio import AsyncAuction
from stalcraft.asyncio.api import AsyncSecretApi, AsyncTokenApi
from stalcraft.client.base import BaseClient
from stalcraft.default import Default
from stalcraft.items import ItemId
from stalcraft.utils import Listing, Method, Params


class AsyncBaseClient(BaseClient):
    _TOKEN_API = AsyncTokenApi
    _SECRET_API = AsyncSecretApi

    def __init__(
        self,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        self.base_url = base_url
        self.json = json

        self._api = self._get_api()

    @abstractmethod
    def _get_api(self) -> _TOKEN_API | _SECRET_API:
        ...

    async def regions(self) -> Any | list[schemas.RegionInfo]:
        response = await self._api.request_get(
            Method("regions")
        )

        return response if self.json else [schemas.RegionInfo.parse_obj(region) for region in response]

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
            Method(region, "emission")
        )

        return response if self.json else schemas.Emission.parse_obj(response)

    async def character_profile(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | schemas.CharacterProfile:
        response = await self._api.request_get(
            Method(region, "character", "by-name", character, "profile")
        )

        return response if self.json else schemas.CharacterProfile.parse_obj(response)

    async def clans(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        region: Region = Default.REGION
    ) -> Any | Listing[schemas.ClanInfo]:
        response = await self._api.request_get(
            Method(region, "clans"),
            Params(limit=limit, offset=offset)
        )

        return response if self.json else Listing(response, schemas.ClanInfo, "data", "totalClans")
