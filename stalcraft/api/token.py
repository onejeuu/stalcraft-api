import base64
import json
from typing import Any, Dict, TypeAlias

from stalcraft.api.base import BaseApi, RequestHeaders
from stalcraft.exceptions import InvalidToken


TokenPayload: TypeAlias = Dict[str, Any]


class TokenApi(BaseApi):
    def __init__(self, token: str, base_url: str):
        super().__init__(base_url)

        self._token = token
        self._token_payload: TokenPayload = {}

        self.validate_token()

    @property
    def part_of_token(self) -> str:
        return f"{self._token[:10]}...{self._token[-5:]}"

    @property
    def headers(self) -> RequestHeaders:
        return {
            "Authorization": f"Bearer {self._token}",
            "Content-Type": "application/json"
        }

    def _parse_jwt_token(self) -> TokenPayload:
        try:
            token_payload = self._token.split('.')[1]
            token_payload_decoded = str(base64.b64decode(f"{token_payload}=="), "utf-8")
            payload = json.loads(token_payload_decoded)

        except Exception:
            raise InvalidToken(f"Invalid token provided: '{self.part_of_token}'")

        else:
            return payload

    def validate_token(self) -> TokenPayload:
        """
        Validate JWT token payload

        Returns:
            TokenPayload: Dict[str, Any]

        Raises:
            InvalidToken: If token is invalid
        """

        payload = self._parse_jwt_token()

        self._token_payload = payload

        return payload

    def __str__(self):
        return f"{super().__str__()} token='{self.part_of_token}'"
