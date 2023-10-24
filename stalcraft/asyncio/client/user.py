from pathlib import Path
from typing import Any

from stalcraft import Region
from stalcraft import exceptions as exc
from stalcraft import schemas
from stalcraft.asyncio.api import AsyncTokenApi
from stalcraft.asyncio.clan import AsyncUserClan
from stalcraft.asyncio.client.base import AsyncBaseClient
from stalcraft.client.user import UserClient
from stalcraft.defaults import Default


class AsyncUserClient(UserClient, AsyncBaseClient):
    def _get_api(self):
        if self._token:
            return AsyncTokenApi(self._token, self.base_url)

        raise exc.MissingCredentials("No token provided.")

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION
    ) -> AsyncUserClan:
        return AsyncUserClan(self._api, clan_id, region, self.json)

    async def characters(
        self,
        region: Region = Default.REGION
    ) -> Any | list[schemas.Character]:
        response = await self._api.request_get(
            Path(region, "characters")
        )

        return response if self.json else [schemas.Character.parse_obj(character) for character in response]

    async def friends(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | list[str]:
        response = await self._api.request_get(
            Path(region, "friends", character)
        )

        return response
