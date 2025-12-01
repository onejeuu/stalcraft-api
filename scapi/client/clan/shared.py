from typing import Optional

from scapi.client import models
from scapi.config import Config
from scapi.consts import Defaults
from scapi.enums import Region
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient


class ClanEndpoint(APIClient):
    """Endpoint for public clan information."""

    def __init__(
        self,
        *,
        http: HTTPClient,
        clan_id: str,
        json: bool = Defaults.JSON,
    ):
        """
        Initialize clan endpoint.

        Args:
            http: HTTP client instance.
            clan_id: Clan identifier.
            json (optional): Return JSON instead of models. Defaults to `False`.
        """

        self._http = http
        self._clan_id = clan_id
        self._json = json

    async def info(
        self,
        region: Optional[str | Region] = None,
    ) -> models.ClanInfo:
        """
        Retrieve clan information.

        Args:
            region (optional): Game server region. Defaults to `RU`.

        Returns:
            Clan details.
        """

        region = region or Config.REGION

        response = await self._http.GET(
            f"{region}/clan/{self._clan_id}/info",
        )

        return self._parse(response, models.ClanInfo)

    def __repr__(self):
        return f"{self.__class__.__name__}(clan_id='{self._clan_id}', http={self._http})"
