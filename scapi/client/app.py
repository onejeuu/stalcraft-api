import warnings
from typing import Optional

from scapi import exceptions
from scapi.consts import BaseUrl, Defaults
from scapi.http.auth.creds import CredentialsHTTPClient
from scapi.http.auth.token import TokenHTTPClient

from .clan.shared import ClanEndpoint
from .shared import SharedClient


class AppClient(SharedClient):
    """API Client for application specific endpoints."""

    def __init__(
        self,
        *,
        token: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = BaseUrl.PRODUCTION,
        timeout: int = Defaults.TIMEOUT,
        json: bool = Defaults.JSON,
    ):
        """
        Initialize application client with authentication credentials.

        **Note:** Provide EITHER token OR both client_id and client_secret.

        Args:
            token (optional): Created application token.
            client_id (optional): Application client identifier.
            client_secret (optional): Application client secret.
            base_url (optional): API server base URL. Defaults to `http://eapi.stalcraft.net`.
            timeout (optional): Request timeout in seconds. Defaults to `60s`.
            json (optional): Return JSON instead of models. Defaults to `False`.
        """

        self._token = token
        self._client_id = client_id
        self._client_secret = client_secret
        self._timeout = timeout

        super().__init__(base_url=base_url, json=json)

        if token and (client_id or client_secret):
            warnings.warn("Redundant auth parameters. Provide EITHER 'token' OR both 'client_id' and 'client_secret'.")

    def _create_http_client(self):
        if self._client_id and self._client_secret:
            return CredentialsHTTPClient(
                client_id=self._client_id,
                client_secret=self._client_secret,
                base_url=self._base_url,
                timeout=self._timeout,
            )

        if self._token:
            return TokenHTTPClient(
                token=self._token,
                base_url=self._base_url,
                timeout=self._timeout,
            )

        raise exceptions.CredentialsError(
            f"Missing required credentials for {self.__class__.__name__}. "
            "Provide EITHER 'token' OR both 'client_id' and 'client_secret'."
        )

    def clan(
        self,
        clan_id: str,
    ) -> ClanEndpoint:
        """
        Factory method for clan endpoint.

        Args:
            clan_id: Clan identifier.

        Returns:
            Clan endpoint instance.
        """

        return ClanEndpoint(clan_id=clan_id, http=self._http, json=self._json)
