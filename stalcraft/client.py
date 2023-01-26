from . import AppClan, Auction, BaseApi, BaseUrl, Region, UserClan, Rank
from . import schemas


class Client(BaseApi):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        """
        Client for working with the API.

        Args:
            token: Token for authorization
            base_url: Optional parameter, API url
        """

        super().__init__(token, base_url)

    def regions(self):
        """
        Returns list of regions which can be access by api calls.
        """

        method = "regions"
        response = self._request(method)

        return [
            schemas.RegionInfo(region)
            for region in response
        ]

    def emission(self, region=Region.RU):
        """
        Returns information about current emission, if any, and recorded time of the previous one.

        Args:
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/emission"
        response = self._request(method)

        return schemas.Emission(response)

    def clans(self, offset=0, limit=20, region=Region.RU):
        """
        Returns all clans which are currently registered in the game on specified region.

        Args:
            offset: Amount of clans in list to skip, default 0
            limit: Amount of clans to return, starting from offset, minimum 0, maximum 100, default 20
            region: Stalcraft region, default Region.RU
        """

        self._offset_and_limit(offset, limit)

        method = f"{region.value}/clans"
        payload = {"offset": offset, "limit": limit}
        response = self._request(method, payload)

        return [
            schemas.ClanInfo(clan)
            for clan in response['data']
        ]

    def auction(self, item_id, region=Region.RU):
        """
        Factory method for working with auction

        Args:
            item_id: Item ID, for example "y1q9"
            region: Stalcraft region, default Region.RU
        """

        return Auction(self.token, self.base_url, item_id, region)


class AppClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)
        self.validate_token()

    def clan(self, clan_id: str = "", region=Region.RU):
        """
        Factory method for working with clans

        Args:
            clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region, default Region.RU
        """

        return AppClan(self.token, self.base_url, clan_id, region)


class UserClient(Client):
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
        super().__init__(token, base_url)
        self.validate_token()

    def characters(self, region=Region.RU):
        """
        Returns list of characters created by the user by which used access token was provided.

        Args:
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/characters"
        response = self._request(method)

        return [
            schemas.Character(character)
            for character in response
        ]

    def friends(self, character: str, region=Region.RU):
        """
        Returns list of character names who are friend with specified character.

        Args:
            character: Character name
            region: Stalcraft region, default Region.RU
        """

        method = f"{region.value}/friends/{character}"
        return self._request(method)

    def clan(self, clan_id: str, region=Region.RU):
        """
        Factory method for working with clans

        Args:
            clan_id: Clan ID, for example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region, default Region.RU
        """

        return UserClan(self.token, self.base_url, clan_id, region)
