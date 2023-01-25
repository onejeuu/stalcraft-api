from datetime import datetime

from . import BaseApi, BaseUrl, Region, Rank
from . import schemas


class Clan(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl, clan_id="", region=Region.RU):
        super().__init__(token, base_url)

        if not clan_id:
            raise ValueError(f"Invalid clan_id: '{clan_id}'")

        self.clan_id = clan_id
        self.region = region

    def info(self):
        """
        Returns information about the given clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/info"
        response = self._request(method)

        return schemas.ClanInfo(response)

    def __repr__(self):
        return f"<Clan> clan_id='{self.clan_id}' region='{self.region}'"


class AppClan(Clan):
    def __init__(self, token, base_url, clan_id, region):
        super().__init__(token, base_url, clan_id, region)

    def __repr__(self):
        return f"<AppClan> clan_id='{self.clan_id}' region='{self.region}'"


class UserClan(Clan):
    def __init__(self, token, base_url, clan_id, region):
        super().__init__(token, base_url, clan_id, region)

    def members(self):
        """
        Returns list of members in the given.

        ! Can be used only when using user access token and that user has at least one character in that clan.
        """

        method = f"{self.region.value}/clan/{self.clan_id}/members"
        response = self._request(method)

        return [
            schemas.ClanMember(member)
            for member in response
        ]

    def __repr__(self):
        return f"<UserClan> clan_id='{self.clan_id}' region='{self.region}'"
