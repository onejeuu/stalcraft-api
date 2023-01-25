from datetime import datetime
import requests

from . import BaseUrl, Unauthorised, InvalidParameter, NotFound


class BaseApi:
    def __init__(self, token: str, base_url: str | BaseUrl = BaseUrl.DEMO):
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

    def _request(self, method: str, params={}):
        """
        Makes request to Stalcraft API with Authorization and Content-Type header
        """

        url = f"{self.base_url}/{method}"

        response = requests.get(
            url=url,
            headers=self.headers,
            params=params
        )

        if response.status_code == 400:
            raise InvalidParameter(f"One of parameters is invalid: '{url}' {params}")

        if response.status_code == 401:
            raise Unauthorised(f"Bad Token: '{self.part_of_token}'")

        if response.status_code == 404:
            raise NotFound(f"Not Found: '{url}' {params}")

        return response.json()

    def _offset_and_limit(self, offset: int, limit: int):
        """
        Validate offset and limit values
        """

        assert offset >= 0, f"offset should be >= 0, got {offset}"
        assert limit in range(0, 101), f"limit should be between 0 and 100, got {limit}"

    def __repr__(self):
        return f"<BaseAPI> base_url='{self.base_url}' token='{self.part_of_token}'"
