from . import BaseApi, BaseUrl, Region


class Clan(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl, clan_id="", region=Region.RU):
        super().__init__(token, base_url)

        if not clan_id:
            raise ValueError(f"Invalid clan_id: '{clan_id}'")

        self.clan_id = clan_id
        self.region = region

    def info(self):
        """
        Returns information about clan
        """

        method = f"{self.region.value}/clan/{self.clan_id}/info"
        return self._request(method)

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
        Returns clan members
        """

        method = f"{self.region.value}/clan/{self.clan_id}/members"
        return self._request(method)

    def __repr__(self):
        return f"<UserClan> clan_id='{self.clan_id}' region='{self.region}'"
