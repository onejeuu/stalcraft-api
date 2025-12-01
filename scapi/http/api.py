from types import TracebackType
from typing import Any, Optional, Self, TypeVar, cast

from pydantic import BaseModel

from scapi.defaults import Default

from .client import HTTPClient
from .ratelimit import RateLimit
from .types import Listing


M = TypeVar("M", bound=BaseModel)


class APIClient:
    _http: HTTPClient
    _json: bool = Default.JSON

    @property
    def ratelimit(self) -> RateLimit:
        """Current ratelimit status."""

        return self._http.ratelimit

    def _parse(
        self,
        response: Any,
        model: Optional[type[M]] = None,
        listing: Optional[tuple[str, str]] = None,
    ) -> Any:
        """Parse http response into models or return raw."""

        if not model or self._json:
            return response

        if listing:
            key_data, key_total = listing
            return Listing(response, model, key_data, key_total)

        if isinstance(response, list):
            response = cast(list[Any], response)
            return [model.model_validate(item) for item in response]

        return model.model_validate(response)

    async def close(self) -> None:
        await self._http.close()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> bool:
        await self.close()
        return False

    def __repr__(self):
        return f"{self.__class__.__name__}(http={self._http})"
