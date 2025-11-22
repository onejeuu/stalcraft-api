from typing import Self

from .client import HTTPClient


class APIClient:
    _http: HTTPClient

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __str__(self):
        return f"<{self.__class__.__name__} http={self._http}>"
