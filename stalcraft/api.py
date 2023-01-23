import requests

from . import BaseUrl


class BaseApi:
    def __init__(self, token: str, base_url: str | BaseUrl = ""):
        assert token is not None, "token should not be None"

        if isinstance(base_url, BaseUrl):
            base_url = base_url.value

        if not base_url:
            base_url = BaseUrl.DEMO.value

        self.base_url = base_url
        self.token = token

    @property
    def part_of_token(self):
        return f"{self.token[:10]}...{self.token[-5:]}"

    @property
    def headers(self):
        return {"Authorization": f"Bearer {self.token}"}

    def _request(self, method: str):
        """
        Makes request to Stalcraft API with Authorization header
        """

        response = requests.get(
            f"{self.base_url}/{method}",
            headers=self.headers
        )
        return response.json()

    def _offset_and_limit(self, offset: int, limit: int):
        """
        Validate offset and limit values
        """

        assert offset >= 0, f"offset should be >= 0, got {offset}"
        assert limit in range(0, 101), f"limit should be between 0 and 100, got {limit}"

    def __repr__(self):
        return f"<BaseAPI> api_link='{self.base_url}' token='{self.part_of_token}'"
