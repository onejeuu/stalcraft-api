from typing import Any, Dict, Literal
from requests import Response
import requests
import base64
import json

from . import (
    BaseUrl, StatusCode,
    InvalidToken, StalcraftApiException, InvalidParameter, Unauthorised, NotFound
)


class BaseApi:
    def __init__(self, token: str, base_url: BaseUrl | str):
        assert token is not None, "token should not be None"

        if isinstance(base_url, BaseUrl):
            base_url = base_url.value

        self.base_url = base_url
        self.token = token

    @property
    def part_of_token(self):
        return f"{self.token[:10]}...{self.token[-5:]}"

    @property
    def headers(self):
        return {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

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
                raise Unauthorised(f"Bad Token: '{self.part_of_token}'")

            case StatusCode.NOT_FOUND.value:
                raise NotFound(f"Not Found: url='{url}' payload={payload}")

            case StatusCode.OK.value:
                return response.json()

            case _:
                raise StalcraftApiException(response)

    def _request(self, method: str, payload: Dict[str, Any]={}) -> Dict[str, Any]:
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
        return f"<{self.__class__.__name__}> base_url='{self.base_url}' token='{self.part_of_token}'"


class Api(BaseApi):
    def __init__(self, token: str, base_url: BaseUrl | str):
        super().__init__(token, base_url)

        self.token_payload = {}

        self.validate_token()

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
