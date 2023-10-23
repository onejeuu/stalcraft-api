from typing import Any

from stalcraft import Region, schemas
from stalcraft.api.base import BaseApi
from stalcraft.utils import Method


class Clan:
    def __init__(
        self,
        api: BaseApi,
        clan_id: str,
        region: Region,
        json: bool
    ):
        self._api = api
        self.clan_id = clan_id
        self.region = region
        self.json = json

    def info(self) -> Any | schemas.ClanInfo:
        """
        Returns information about the given clan.
        """

        response = self._api.request_get(
            Method(self.region, "clan", self.clan_id, "info")
        )

        return response if self.json else schemas.ClanInfo.parse_obj(response)

    def __str__(self):
        return f"<{self.__class__.__name__}> clan_id='{self.clan_id}' region='{self.region}'"
