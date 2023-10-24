import warnings
from typing import Optional

from stalcraft import Region
from stalcraft import exceptions as exc
from stalcraft.api import SecretApi, TokenApi
from stalcraft.clan import Clan
from stalcraft.client.base import BaseClient
from stalcraft.defaults import Default


class AppClient(BaseClient):
    def __init__(
        self,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        """
        App Client for working with the API.

        Args:
            token: App access token.
            client_id: OAuth2 application ID.
            client_secret: OAuth2 application secret.
            base_url (optional): API base url. Defaults to PRODUCTION.
            json (optional): Raw response format. Defaults to False.
        """

        self._token = token
        self._client_id = client_id
        self._client_secret = client_secret

        super().__init__(base_url, json)

        if token and (client_id or client_secret):
            warnings.warn("You should not use [token] and [client_id with client_secret]. Pick one of them.")

    def _get_api(self):
        if self._token:
            return TokenApi(self._token, self._base_url)

        if self._client_id and self._client_secret:
            return SecretApi(self._client_id, self._client_secret, self._base_url)

        raise exc.MissingCredentials("No token or client_id with client_secret provided.")

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION
    ) -> Clan:
        """
        Factory method for working with clans.

        Args:
            clan_id: Clan ID. For example "647d6c53-b3d7-4d30-8d08-de874eb1d845".
            region: Stalcraft server region.
        """

        return Clan(self._api, clan_id, region, self.json)
