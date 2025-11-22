from typing import List

from scapi import exceptions
from scapi.client import models
from scapi.defaults import Default
from scapi.enums import Region
from scapi.http.auth.token import TokenHTTPClient

from .clan.user import UserClanEndpoint
from .shared import SharedClient


class UserClient(SharedClient):
    def __init__(
        self,
        token: str,
        base_url: str = Default.BASE_URL,
        timeout: int = Default.TIMEOUT,
        json: bool = Default.JSON,
    ):
        self._token = token
        self._timeout = timeout

        super().__init__(base_url, json)

    def _create_http_client(self):
        if self._token:
            return TokenHTTPClient(
                token=self._token,
                base_url=self._base_url,
                timeout=self._timeout,
            )

        raise exceptions.CredentialsError("No token provided.")

    async def characters(
        self,
        region: Region = Default.REGION,
    ) -> List[models.Character]:
        response = await self._http.GET(
            url=f"{region}/characters",
        )

        return self._parse(response, models.Character)

    async def friends(
        self,
        character: str,
        region: Region = Default.REGION,
    ) -> List[str]:
        response = await self._http.GET(
            f"{region}/friends/{character}",
        )

        return self._parse(response)

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION,
    ) -> UserClanEndpoint:
        return UserClanEndpoint(self._http, clan_id, region, self._json)
