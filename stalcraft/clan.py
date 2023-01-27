from . import BaseApi, BaseUrl, Region
from . import schemas


class Clan(BaseApi):
    def __init__(self, token: str, base_url: BaseUrl | str, json: bool, clan_id: str, region: Region):
        super().__init__(token, base_url)

        self.json = json

        self.clan_id = clan_id
        self.region = region

    def info(self):
        """
        Returns information about the given clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/info"
        response = self._request(method)

        if self.json is True:
            return response

        return schemas.ClanInfo(response)

    def __repr__(self):
        return f"{super().__repr__()} clan_id='{self.clan_id}' region='{self.region}'"


class AppClan(Clan):
    def __init__(self, token, base_url, json, clan_id, region):
        super().__init__(token, base_url, json, clan_id, region)


class UserClan(Clan):
    def __init__(self, token, base_url, json, clan_id, region):
        super().__init__(token, base_url, json, clan_id, region)

    def members(self):
        """
        Returns list of members in the given clan.

        ! Can be used only when using user access token and that user has at least one character in that clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/members"
        response = self._request(method)

        if self.json is True:
            return response

        return [
            schemas.ClanMember(member)
            for member in response
        ]
