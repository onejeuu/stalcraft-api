from typing import List, Optional

from scapi import exceptions
from scapi.client import models
from scapi.config import Config
from scapi.consts import BaseUrl, Defaults
from scapi.enums import Region
from scapi.http.auth.token import TokenHTTPClient

from .clan.user import UserClanEndpoint
from .shared import SharedClient


class UserClient(SharedClient):
    """API Client for user specific endpoints."""

    def __init__(
        self,
        *,
        token: str,
        base_url: str = BaseUrl.PRODUCTION,
        timeout: int = Defaults.TIMEOUT,
        json: bool = Defaults.JSON,
    ):
        """
        Initialize user client with authentication token.

        Args:
            token: User access token.
            base_url (optional): API server base URL. Defaults to `http://eapi.stalcraft.net`.
            timeout (optional): Request timeout in seconds. Defaults to `60s`.
            json (optional): Return JSON instead of models. Defaults to `False`.
        """

        self._token = token
        self._timeout = timeout

        super().__init__(base_url=base_url, json=json)

    def _create_http_client(self):
        if self._token:
            return TokenHTTPClient(
                token=self._token,
                base_url=self._base_url,
                timeout=self._timeout,
            )

        raise exceptions.CredentialsError(f"No user token provided for {self.__class__.__name__}.")

    async def characters(
        self,
        region: Optional[str | Region] = None,
    ) -> List[models.Character]:
        """
        Retrieve user characters.

        Args:
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            List of user characters.
        """

        region = (region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/characters",
        )

        return self._parse(response, models.Character)

    async def friends(
        self,
        character: str,
        region: Optional[str | Region] = None,
    ) -> List[str]:
        """
        Retrieve user character friends list.

        Args:
            character: User character name.
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            List of user friends character names.
        """

        region = (region or Config.REGION).lower()

        response = await self._http.GET(
            f"{region}/friends/{character}",
        )

        return self._parse(response)

    def clan(
        self,
        clan_id: str,
    ) -> UserClanEndpoint:
        """
        Factory method for user specific clan endpoint.

        Args:
            clan_id: Clan identifier.

        Returns:
            User clan endpoint instance.
        """

        return UserClanEndpoint(clan_id=clan_id, http=self._http, json=self._json)
