from . import AppClan, Auction, BaseApi, BaseUrl, Region, UserClan


class Client(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        """
        token: Token for authorization, you can use DemoToken.APP or DemoToken.USER
        base_url: Optional parameter, API url
        """

        super().__init__(token, base_url)

    def regions(self):
        """
        Returns list of regions
        """

        method = "regions"
        return self._request(method)

    def clans(self, offset=0, limit=20, region=Region.RU):
        """
        Returns list of clans

        offset: Amount of clans in list to skip, default 0
        limit: Amount of clans to return, starting from offset, minimum 0, maximum 100, default 20
        region: Stalcraft region, default Region.RU
        """

        self._offset_and_limit(offset, limit)

        method = f"{region.value}/clans?offset={offset}&limit={limit}"
        return self._request(method)

    def emission(self, region=Region.RU):
        """
        Returns information about emission

        region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/emission"
        return self._request(method)

    def auction(self, item_id="", region=Region.RU):
        """
        Interface for working with auction

        item_id: Item ID, for example "y1q9"
        region: Stalcraft region, default Region.RU
        """

        return Auction(self.token, self.base_url, item_id, region)

    def __repr__(self):
        return f"<Client> api_link='{self.base_url}' token='{self.part_of_token}'"


class AppClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)

    def clan(self, clan_id: str = "", region=Region.RU):
        """
        Interface for working with clans

        clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
        region: Stalcraft region, default Region.RU
        """

        return AppClan(self.token, self.base_url, clan_id, region)

    def __repr__(self):
        return f"<AppClient> api_link='{self.base_url}' token='{self.part_of_token}'"


class UserClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)

    def characters(self, region=Region.RU):
        """
        Returns list of your characters

        region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/characters"
        return self._request(method)

    def friends(self, character="", region=Region.RU):
        """
        Returns list of characters friends

        character: Character name
        region: Stalcraft region, default Region.RU
        """

        if not character:
            raise ValueError(f"Invalid character '{character}'")

        method = f"{region.value}/friends/{character}"
        return self._request(method)

    def clan(self, clan_id="", region=Region.RU):
        """
        Interface for working with clans

        clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
        region: Stalcraft region, default Region.RU
        """

        return UserClan(self.token, self.base_url, clan_id, region)

    def __repr__(self):
        return f"<UserClient> api_link='{self.base_url}' token='{self.part_of_token}'"
