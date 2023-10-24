from stalcraft import Region
from stalcraft import exceptions as exc
from stalcraft.asyncio.api import AsyncSecretApi, AsyncTokenApi
from stalcraft.asyncio.clan import AsyncClan
from stalcraft.asyncio.client.base import AsyncBaseClient
from stalcraft.client import AppClient
from stalcraft.defaults import Default


class AsyncAppClient(AppClient, AsyncBaseClient):
    """
    Async App Client for working with the API.

    Args:
        token: App access token.
        client_id: Application ID.
        client_secret: Application secret.
        base_url (optional): API base url. Defaults to PRODUCTION.
        json (optional): if True response returned in raw format. Defaults to False.
    """

    def _get_api(self):
        if self._token:
            return AsyncTokenApi(self._token, self.base_url)

        if self._client_id and self._client_secret:
            return AsyncSecretApi(self._client_id, self._client_secret, self.base_url)

        raise exc.MissingCredentials("No token or client_id with client_secret provided.")

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION
    ) -> AsyncClan:
        return AsyncClan(self._api, clan_id, region, self.json)
