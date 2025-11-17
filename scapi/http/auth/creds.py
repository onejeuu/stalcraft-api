from scapi.defaults import Default
from scapi.http.client import HTTPClient


class CredentialsHTTPClient(HTTPClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = Default.BASE_URL,
        timeout: int = Default.TIMEOUT,
    ):
        super().__init__(base_url, timeout)

        self._client_id = client_id
        self._client_secret = client_secret

        self._headers.update(
            {
                "Client-Id": self._client_id,
                "Client-Secret": self._client_secret,
                "Content-Type": "application/json",
            }
        )
