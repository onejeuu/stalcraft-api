from abc import ABC, abstractproperty
from pathlib import Path
from typing import Any, Dict, Optional, TypeAlias, TypedDict

import httpx

from stalcraft import exceptions as exc
from stalcraft.consts import StatusCode
from stalcraft.defaults import Default
from stalcraft.schemas import RateLimit


RequestHeaders: TypeAlias = Dict[str, str]


class HttpxConfig(TypedDict):
    base_url: str
    timeout: httpx.Timeout


class BaseApi(ABC):
    def __init__(self, base_url: str):
        self._base_url = base_url
        self._ratelimit = RateLimit.construct()

    @abstractproperty
    def headers(self) -> RequestHeaders:
        return {}

    @property
    def ratelimit(self) -> RateLimit:
        return self._ratelimit

    @property
    def _timeout(self):
        return httpx.Timeout(Default.TIMEOUT_SECONDS)

    @property
    def _httpx_config(self) -> HttpxConfig:
        return {"base_url": self._base_url, "timeout": self._timeout}

    def _parse_response(self, response: httpx.Response) -> Any:
        validate_status_code(response)
        self._ratelimit = RateLimit.parse_obj(response.headers)
        return response.json()

    def request_get(self, url: Path, params: Optional[httpx.QueryParams] = None) -> Any:
        """
        Makes GET request to Stalcraft API
        """

        with httpx.Client(**self._httpx_config) as client:
            response = client.get(url=url.as_posix(), params=params, headers=self.headers)

        return self._parse_response(response)

    def __str__(self):
        return f"<{self.__class__.__name__}> base_url='{self._base_url}'"


def validate_status_code(response: httpx.Response) -> None:
    match response.status_code:
        case StatusCode.OK:
            pass

        case StatusCode.UNAUTHORISED:
            raise exc.RequestUnauthorised()

        case StatusCode.INVALID_PARAMETER:
            raise exc.RequestInvalidParameter()

        case StatusCode.NOT_FOUND:
            raise exc.RequestNotFound()

        case StatusCode.RATE_LIMIT:
            raise exc.RateLimitReached()

        case _:
            raise exc.ApiRequestError(response)
