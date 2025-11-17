from typing import List, Optional

from scapi import models
from scapi.defaults import Default
from scapi.enums import Region
from scapi.http.auth.token import TokenHTTPClient

from .base import BaseClient
from .clan.user import UserClan


class UserClient(BaseClient):
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = Default.BASE_URL,
        timeout: int = Default.TIMEOUT,
    ):
        self._token = token
        self._timeout = timeout

        super().__init__(base_url)

    def _create_http_client(self):
        if self._token:
            return TokenHTTPClient(
                token=self._token,
                base_url=self._base_url,
                timeout=self._timeout,
            )

        raise Exception("No token provided.")

    async def characters(
        self,
        region: Region = Default.REGION,
    ) -> List[models.api.Character]:
        response = await self._http.GET(
            url=f"{region}/characters",
        )

        return [models.api.Character.model_validate(character) for character in response]

    async def friends(
        self,
        character: str,
        region: Region = Default.REGION,
    ) -> List[str]:
        response = await self._http.GET(
            f"{region}/friends/{character}",
        )

        return response

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION,
    ) -> UserClan:
        return UserClan(self._http, clan_id, region)
