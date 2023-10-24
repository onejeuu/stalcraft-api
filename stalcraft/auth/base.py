from abc import ABC
from typing import Any, Dict

import httpx

from stalcraft.api.base import validate_status_code
from stalcraft.defaults import Default


class BaseAuth(ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str = Default.SCOPE,
        redirect_uri: str = Default.REDIRECT_URI,
        json: bool = Default.JSON
    ):
        """
        Constructor for Authorization.

        Args:
            client_id: OAuth2 client ID.
            client_secret: OAuth2 client secret.
            scope (optional): Authorization scope requested by the client. Defaults to "".
            redirect_uri (optional): URI to redirect the user to after authorization. Defaults to "http://localhost".
            json (optional): if True response returned in raw format. Defaults to True.
        """

        self._client_id = client_id
        self._client_secret = client_secret
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.json = json

    def _request_get(self, url: str, headers: Dict[str, Any]) -> Any:
        with httpx.Client() as client:
            response = client.get(url=url, headers=headers)

        validate_status_code(response)

        return response.json()

    def _request_post(self, url: str, data: Dict[str, Any]) -> Any:
        with httpx.Client() as client:
            response = client.post(url=url, data=data)

        validate_status_code(response)

        return response.json()

    def __str__(self):
        return f"<{self.__class__.__name__}> client_id='{self._client_id}' redirect_uri='{self.redirect_uri}'"
