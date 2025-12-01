from typing import Optional

from scapi.defaults import Default
from scapi.http.client import Headers, HTTPClient


class CredentialsHTTPClient(HTTPClient):
    """HTTP client with client credentials authentication."""

    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = Default.BASE_URL,
        timeout: int = Default.TIMEOUT,
        headers: Optional[Headers] = None,
    ):
        super().__init__(base_url=base_url, timeout=timeout)

        self._client_id = client_id
        self._client_secret = client_secret

        if headers:
            self._headers.update(headers)

        self._headers.update(
            {
                "Client-Id": self._client_id,
                "Client-Secret": self._client_secret,
                "Content-Type": "application/json",
            }
        )
