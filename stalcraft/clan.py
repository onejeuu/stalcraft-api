from . import TokenApi, SecretApi, Region
from . import schemas


class Clan:
    def __init__(self, api: TokenApi | SecretApi, clan_id: str, region: Region, json: bool):
        self._api = api
        self.clan_id = clan_id
        self.region = region
        self.json = json

    def info(self):
        """
        Returns information about the given clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/info"
        response = self._api._request(method)

        if self.json is True:
            return response

        return schemas.ClanInfo.parse_obj(response)

    def __str__(self):
        return f"<{self.__class__.__name__}> {self._api.__str__()} clan_id='{self.clan_id}' region='{self.region}'"


class UserClan(Clan):
    def members(self):
        """
        Returns list of members in the given clan.

        ! Can be used only when using user access token and that user has at least one character in that clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/members"
        response = self._api._request(method)

        if self.json is True:
            return response

        return [
            schemas.ClanMember.parse_obj(member)
            for member in response
        ]
