import base64
import json
from typing import Any, Dict, TypeAlias

from scapi.defaults import Default
from scapi.http.client import HTTPClient


TokenPayload: TypeAlias = Dict[str, Any]


class BearerTokenClient(HTTPClient):
    def __init__(
        self,
        token: str,
        base_url: str,
        timeout: int = Default.TIMEOUT,
    ):
        super().__init__(base_url, timeout)

        self._payload: TokenPayload = {}
        self._token = self._validate_token(token)

        self._headers.update(
            {
                "Authorization": f"Bearer {self._token}",
                "Content-Type": "application/json",
            }
        )

    @property
    def token_part(self) -> str:
        return f"{self._token[:10]}...{self._token[-5:]}"

    def update_token(self, new_token: str) -> None:
        self._token = self._validate_token(new_token)
        self._headers["Authorization"] = f"Bearer {self._token}"

    def _parse_jwt(self, token: str) -> TokenPayload:
        try:
            body = token.split(".")[1]
            decoded = base64.b64decode(f"{body}==")
            data = json.loads(decoded.decode())

        except Exception:
            raise Exception(f"Invalid token provided: '{self.token_part}'")

        else:
            return data

    def _validate_token(self, token: str) -> str:
        self._payload = self._parse_jwt(token)
        return token
