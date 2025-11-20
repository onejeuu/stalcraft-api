from typing import Any, Dict, Optional, TypeAlias

from scapi.defaults import Default
from scapi.http.base import Headers
from scapi.http.client import HTTPClient


TokenPayload: TypeAlias = Dict[str, Any]


class TokenHTTPClient(HTTPClient):
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = "",
        timeout: int = Default.TIMEOUT,
        headers: Optional[Headers] = None,
    ):
        super().__init__(base_url, timeout)

        self._token = token
        self._payload: TokenPayload = {}

        self._headers.update({"Content-Type": "application/json"})

        if headers:
            self._headers.update(headers)

        if token:
            self._payload = self._validate_token(token)
            self._headers.update({"Authorization": f"Bearer {self._token}"})

    @property
    def token_part(self) -> str:
        return str(self._token and f"{self._token[:10]}...{self._token[-5:]}")

    def update_token(self, new_token: str) -> None:
        self._token = new_token
        self._payload = self._validate_token(new_token)
        self._headers["Authorization"] = f"Bearer {self._token}"

    def _validate_token(self, token: str) -> Any:
        return None
