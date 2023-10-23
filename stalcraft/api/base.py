from abc import ABC, abstractproperty
from typing import Any, Dict, Tuple, TypeAlias

import httpx

from stalcraft import exceptions as exc
from stalcraft.consts import StatusCode
from stalcraft.default import Default
from stalcraft.schemas import RateLimit
from stalcraft.utils import Method, Params


RequestParams: TypeAlias = Dict[str, Any]
RequestHeaders: TypeAlias = Dict[str, str]


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

    def _parse_request_args(self, method: str | Method, params: RequestParams | Params) -> Tuple[str, RequestParams]:
        if isinstance(method, Method):
            method = method.parse()

        if isinstance(params, Params):
            params = params.parse()

        return method, params

    def _update_rate_limit(self, headers: httpx.Headers) -> None:
        self._ratelimit = RateLimit.parse_obj(headers)

    def request_get(self, method: str | Method, params: RequestParams | Params = {}) -> Any:
        """
        Makes GET request to Stalcraft API
        """

        method, params = self._parse_request_args(method, params)

        with httpx.Client(base_url=self._base_url, timeout=self._timeout) as client:
            response = client.get(url=method, params=params, headers=self.headers)

        validate_status_code(response)
        self._update_rate_limit(response.headers)

        return response.json()

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
