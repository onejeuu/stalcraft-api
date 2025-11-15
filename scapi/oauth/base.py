from abc import ABC

from scapi.defaults import Default
from scapi.http.client import HTTPClient


class BaseOAuth(ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        scope: str = Default.SCOPE,
        redirect_uri: str = Default.REDIRECT_URI,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self.scope = scope
        self.redirect_uri = redirect_uri

        self._http = HTTPClient()
