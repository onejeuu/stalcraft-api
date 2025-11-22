from scapi.client import models
from scapi.defaults import Default
from scapi.enums import Region
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient


class ClanEndpoint(APIClient):
    def __init__(
        self,
        http: HTTPClient,
        clan_id: str,
        region: Region = Default.REGION,
    ):
        self._http = http
        self._clan_id = clan_id
        self._region = region

    async def info(
        self,
    ) -> models.ClanInfo:
        response = await self._http.GET(
            f"{self._region}/clan/{self._clan_id}/info",
        )

        return models.ClanInfo.model_validate(response)

    def __str__(self):
        return f"<{self.__class__.__name__} clan_id='{self._clan_id}' region='{self._region}' http={self._http}>"
