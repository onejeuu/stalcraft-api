from scapi.client import models
from scapi.defaults import Default
from scapi.enums import Region
from scapi.http.client import HTTPClient


class ClanEndpoint:
    def __init__(
        self,
        http: HTTPClient,
        clan_id: str,
        region: Region = Default.REGION,
    ):
        self._http = http
        self.clan_id = clan_id
        self.region = region

    async def info(self) -> models.ClanInfo:
        response = await self._http.GET(
            f"{self.region}/clan/{self.clan_id}/info",
        )

        return models.ClanInfo.model_validate(response)
