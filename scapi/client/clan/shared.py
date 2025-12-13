from typing import Optional

from scapi.client import models
from scapi.config import Config
from scapi.consts import Defaults
from scapi.enums import Region
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient


class ClanEndpoint(APIClient):
    """Clan endpoint for specified clan."""

    def __init__(
        self,
        *,
        http: HTTPClient,
        clan_id: str,
        json: bool = Defaults.JSON,
        region: Optional[Region | str] = None,
    ):
        """
        Initialize clan endpoint.

        Args:
            http: HTTP client instance.
            clan_id: Clan identifier.
            json (optional): Return JSON instead of models. Defaults to `False`.
            region (optional): Default game server region. Defaults to `ru`.
        """

        self._http = http
        self._clan_id = clan_id
        self._json = json
        self._region = region

    async def info(
        self,
        region: Optional[Region | str] = None,
    ) -> models.ClanInfo:
        """
        Retrieve clan information.

        Args:
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Clan details.
        """

        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            f"{region}/clan/{self._clan_id}/info",
        )

        return self._parse(response, models.ClanInfo)

    def __repr__(self):
        return f"{self.__class__.__name__}(clan_id='{self._clan_id}', http={self._http})"
