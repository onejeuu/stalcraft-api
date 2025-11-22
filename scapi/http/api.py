from typing import Self

from .client import HTTPClient


class BaseAPIClient:
    _http: HTTPClient

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
