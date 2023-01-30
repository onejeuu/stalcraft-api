from typing import Any, Dict, Literal
from requests import Response
import requests
import base64
import json

from . import BaseUrl, StatusCode

from .exceptions import (
    InvalidToken, StalcraftApiException, InvalidParameter, Unauthorised, NotFound
)


class BaseApi:
    def __init__(self, base_url: BaseUrl | str):
        if isinstance(base_url, BaseUrl):
            base_url = base_url.value

        self.base_url = base_url

    @property
    def headers(self):
        return {}

    def _get_response(self, url: str, payload: Dict[str, Any]) -> Response:
        """
        Returns response from Stalcraft API
        """

        return requests.get(
            url=url,
            params=payload,
            headers=self.headers
        )

    def _handle_response_status(self, response: Response, url: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match response status_code
        """

        match response.status_code:
            case StatusCode.INVALID_PARAMETER.value:
                raise InvalidParameter(f"One of parameters is invalid: url='{url}' payload={payload}")

            case StatusCode.UNAUTHORISED.value:
                raise Unauthorised("Bad token or client_id and client_secret")

            case StatusCode.NOT_FOUND.value:
                raise NotFound(f"Not Found: url='{url}' payload={payload}")

            case StatusCode.OK.value:
                return response.json()

            case _:
                raise StalcraftApiException(response)

    def _request(self, method: str, payload: Dict[str, Any]={}) -> Any:
        """
        Makes request to Stalcraft API
        """

        url = f"{self.base_url}/{method}"

        response = self._get_response(url, payload)
        result = self._handle_response_status(response, url, payload)

        return result

    def _offset_and_limit(self, offset: int, limit: int):
        """
        Validate offset and limit values
        """

        assert offset >= 0, f"offset should be >= 0, got {offset}"
        assert limit in range(0, 101), f"limit should be between 0 and 100, got {limit}"

    def __repr__(self):
        return f"base_url='{self.base_url}'"


class TokenApi(BaseApi):
    def __init__(self, token: str, base_url: BaseUrl | str):
        super().__init__(base_url)

        self.token = token

        self.token_payload = {}

        self.validate_token()

    @property
    def part_of_token(self):
        if self.token:
            return f"{self.token[:10]}...{self.token[-5:]}"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

    def _parse_jwt_token(self) -> Literal[False] | Dict[str, Any]:
        try:
            token_payload = self.token.split('.')[1]
            token_payload_decoded = str(base64.b64decode(token_payload + "=="), "utf-8")
            payload = json.loads(token_payload_decoded)

        except Exception:
            return False

        else:
            return payload

    def validate_token(self) -> Dict[str, Any]:
        """
        Validate JWT token payload
        """

        payload = self._parse_jwt_token()

        if payload is False:
            raise InvalidToken(f"Invalid token provided: '{self.part_of_token}'")

        self.token_payload = payload
        return payload

    def __repr__(self):
        return f"{super().__repr__()} token='{self.part_of_token}'"


class SecretApi(BaseApi):
    def __init__(self, client_id: str, client_secret: str, base_url: BaseUrl | str):
        super().__init__(base_url)

        self.client_id = client_id
        self.client_secret = client_secret

    @property
    def part_of_secret(self):
        return f"{self.client_secret[:5]}...{self.client_secret[-3:]}"

    @property
    def headers(self):
        return {
            "Client-Id": self.client_id,
            "Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }

    def __repr__(self):
        return f"{super().__repr__()} client_id='{self.client_id}' client_secret='{self.part_of_secret}'"
