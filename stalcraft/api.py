from . import ApiLink

from typing import Any
import requests


class BaseApi:
    def __init__(self, token: str, api_link: str | ApiLink = ""):
        assert token is not None, "token should not be None"

        if not api_link:
            api_link = ApiLink.DEMO.value

        self.api_link = api_link
        self.token = token

    @property
    def token_part(self) -> str:
        return f"{self.token[0:15]}..."

    @property
    def headers(self) -> dict:
        """
        Возвращает header для авторизации
        """

        return {"Authorization": f"Bearer {self.token}"}

    def _request(self, method: str) -> Any:
        """
        Делает запрос в API
        """

        response = requests.get(
            f"{self.api_link}/{method}",
            headers=self.headers
        )
        return response.json()

    def _offset_and_limit(self, offset: int, limit: int) -> None:
        """
        Проверяет правильность значений offset и limit
        """

        assert offset >= 0, f"offset should be >= 0, got {offset}"
        assert limit in range(0, 101), f"limit should be between 0 and 100, got {limit}"

    def __repr__(self):
        return f"<BaseAPI> api_link='{self.api_link}' token='{self.token_part}'"
