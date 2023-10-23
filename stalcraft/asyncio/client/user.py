from typing import Any

from stalcraft import Region
from stalcraft import exceptions as exc
from stalcraft import schemas
from stalcraft.asyncio.clan import AsyncUserClan
from stalcraft.asyncio.client.base import AsyncBaseClient
from stalcraft.client.user import UserClient
from stalcraft.default import Default
from stalcraft.utils import Method


class AsyncUserClient(UserClient, AsyncBaseClient):
    """
    Async User Client for working with the API.

    Args:
        token: User access token.
        base_url (optional): API base url. Defaults to PRODUCTION.
        json (optional): if True response returned in raw format. Defaults to False.
    """

    def _get_api(self):
        if self._token:
            return self._TOKEN_API(self._token, self.base_url)

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
            Method(region, "characters")
        )

        return response if self.json else [schemas.Character.parse_obj(character) for character in response]

    async def friends(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | list[str]:
        response = await self._api.request_get(
            Method(region, "friends", character)
        )

        return response
