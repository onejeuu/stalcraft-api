from typing import Any

from stalcraft import Clan, Region, schemas
from stalcraft.asyncio.api.base import AsyncBaseApi
from stalcraft.utils import Method


class AsyncClan(Clan):
    def __init__(
        self,
        api: AsyncBaseApi,
        clan_id: str,
        region: Region,
        json: bool
    ):
        super().__init__(api, clan_id, region, json)
        self._api = api

    async def info(self) -> Any | schemas.ClanInfo:
        response = await self._api.request_get(
            Method(self.region, "clan", self.clan_id, "info")
        )

        return response if self.json else schemas.ClanInfo.parse_obj(response)
