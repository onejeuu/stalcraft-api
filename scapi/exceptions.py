from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Self

from yarl import URL


class ScApiException(Exception):
    """Base exception for `scapi` errors."""

    pass


class ClientError(ScApiException):
    """Client request related error."""

    pass


class CredentialsError(ClientError):
    """Client missing credentials."""

    pass


@dataclass
class RequestError(ClientError):
    """HTTP request error."""

    data: Any
    status: int
    method: str
    url: URL

    _registry: ClassVar[dict[int, type[Self]]] = {}

    def __init_subclass__(cls, codes: Optional[set[int]] = None, **kwargs):
        super().__init_subclass__(**kwargs)
        if codes:
            for code in codes:
                cls._registry[code] = cls

    @property
    def message(self) -> str:
        return str(self.data)[:500]

    def __str__(self):
        return f"HTTP {self.status} - {self.message}"


class BadRequestError(RequestError, codes={400}):
    """Invalid request parameters or malformed data."""

    pass


class UnauthorizedError(RequestError, codes={401}):
    """Missing or invalid authentication credentials."""

    pass


class NotFoundError(RequestError, codes={404}):
    """Requested resource not found."""

    pass


class RateLimitError(RequestError, codes={429}):
    """API rate limit exceeded."""

    pass


class ServerError(RequestError, codes={500, 502, 503, 504}):
    """Server-side error during request."""

    pass
