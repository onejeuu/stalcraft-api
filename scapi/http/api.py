from typing import Any, Optional, Self, TypeVar

from pydantic import BaseModel

from .client import HTTPClient
from .types import Listing


M = TypeVar("M", bound=BaseModel)
T = TypeVar("T")


class APIClient:
    _http: HTTPClient
    _json: bool = False

    def _parse(
        self,
        response: Any,
        model: Optional[type[M]] = None,
        listing: Optional[tuple[str, str]] = None,
    ) -> Any:
        if not model or self._json:
            return response

        if listing:
            key_data, key_total = listing
            return Listing(response, model, key_data, key_total)

        if isinstance(response, list):
            return [model.model_validate(item) for item in response]

        return model.model_validate(response)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    def __str__(self):
        return f"<{self.__class__.__name__} http={self._http}>"
