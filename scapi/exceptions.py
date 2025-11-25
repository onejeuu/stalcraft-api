from dataclasses import dataclass
from typing import Any, ClassVar, Optional, Self

from yarl import URL


class ScApiException(Exception):
    pass


class ClientError(ScApiException):
    pass


class CredentialsError(ClientError):
    pass


@dataclass
class RequestError(ClientError):
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
    pass


class UnauthorizedError(RequestError, codes={401}):
    pass


class NotFoundError(RequestError, codes={404}):
    pass


class RateLimitError(RequestError, codes={429}):
    pass


class ServerError(RequestError, codes={500, 502, 503, 504}):
    pass
