from . import Auction, BaseUrl, Clan, LocalItem, Region, SecretApi, TokenApi, UserClan, WebItem
from . import schemas


class Client:
    def __init__(
        self,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: BaseUrl | str = BaseUrl.PRODUCTION,
        json = False
    ):
        self.token = token
        self.client_id = client_id
        self.client_secret = client_secret
        self.base_url = base_url
        self.json = json

        if token:
            self._api = TokenApi(token, base_url)

        elif client_id and client_secret:
            self._api = SecretApi(client_id, client_secret, base_url)

        else:
            raise ValueError("No token or client_id with client_secret provided.")

    @property
    def ratelimit(self):
        return self._api._ratelimit

    def regions(self):
        """
        Returns list of regions which can be access by api calls.
        """

        method = "regions"
        response = self._api._request(method)

        if self.json is True:
            return response

        return [
            schemas.RegionInfo(region)
            for region in response
        ]

    def emission(self, region=Region.RU):
        """
        Returns information about current emission, if any, and recorded time of the previous one.

        Args:
            region: Stalcraft region. Defaults to RU
        """

        method = f"{region.value}/emission"
        response = self._api._request(method)

        if self.json is True:
            return response

        return schemas.Emission(response)

    def clans(self, offset=0, limit=20, region=Region.RU):
        """
        Returns all clans which are currently registered in the game on specified region.

        Args:
            offset: Amount of clans in list to skip. Defaults to 0
            limit: Amount of clans to return, starting from offset, (0-100). Defaults to 20
            region: Stalcraft region. Defaults to RU
        """

        self._api._offset_and_limit(offset, limit)

        method = f"{region.value}/clans"
        payload = {"offset": offset, "limit": limit}
        response = self._api._request(method, payload)

        if self.json is True:
            return response

        return [
            schemas.ClanInfo(clan)
            for clan in response['data']
        ]

    def auction(self, item_id: str | LocalItem | WebItem, region=Region.RU):
        """
        Factory method for working with auction.

        Args:
            item_id: Item ID. For example "1r756"
            region: Stalcraft region. Defaults to RU
        """

        return Auction(self._api, item_id, region, self.json)

    def character_profile(self, character: str, region=Region.RU):
        """
        Returns information about player's profile.
        Includes alliance, profile description, last login time, stats, etc.

        Args:
            character: Character name
            region: Stalcraft region. Defaults to RU
        """

        method = f"{region.value}/character/by-name/{character}/profile"
        response = self._api._request(method)

        if self.json is True:
            return response

        return schemas.CharacterProfile(response)

    def __repr__(self):
        return f"<{self.__class__.__name__}> {self._api.__repr__()}"


class AppClient(Client):
    def __init__(
        self,
        token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        base_url: BaseUrl | str = BaseUrl.PRODUCTION,
        json = False
    ):
        """
        App Client for working with the API.

        Args:
            token: App access token for authorization
            client_id: Application ID for authorization
            client_secret: Application secret for authorization
            base_url (optional): API base URL. Defaults to PRODUCTION
            json (optional): if True response returned in raw format. Defaults to False
        """

        super().__init__(token, client_id, client_secret, base_url, json)


    def clan(self, clan_id: str, region=Region.RU):
        """
        Factory method for working with clans.

        Args:
            clan_id: Clan ID. For example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region. Defaults to RU
        """

        return Clan(self._api, clan_id, region, self.json)


class UserClient(Client):
    def __init__(
        self,
        token: str,
        base_url: BaseUrl | str = BaseUrl.PRODUCTION,
        json = False
    ):
        """
        User Client for working with the API.

        Args:
            token: User access token for authorization
            base_url (optional): API base URL. Defaults to PRODUCTION
            json (optional): if True response returned in raw format. Defaults to False
        """

        super().__init__(token=token, base_url=base_url, json=json)

    def characters(self, region=Region.RU):
        """
        Returns list of characters created by the user by which used access token was provided.

        Args:
            region: Stalcraft region. Defaults to RU
        """

        method = f"{region.value}/characters"
        response = self._api._request(method)

        if self.json is True:
            return response

        return [
            schemas.Character(character)
            for character in response
        ]

    def friends(self, character: str, region=Region.RU):
        """
        Returns list of character names who are friend with specified character.

        Args:
            character: Character name
            region: Stalcraft region. Defaults to RU
        """

        method = f"{region.value}/friends/{character}"
        response = self._api._request(method)

        return list(response)

    def clan(self, clan_id: str, region=Region.RU):
        """
        Factory method for working with clans.

        Args:
            clan_id: Clan ID. For example "647d6c53-b3d7-4d30-8d08-de874eb1d845"
            region: Stalcraft region. Defaults to RU
        """

        return UserClan(self._api, clan_id, region, self.json)
