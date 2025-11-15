from typing import Any, Dict, Optional, TypeAlias
from urllib.parse import urljoin

import aiohttp
from pydantic import ValidationError

from scapi.defaults import Default

from .params import Params
from .ratelimit import RateLimit


Headers: TypeAlias = Dict[str, str]

JsonData: TypeAlias = Dict[str, Any]
Data: TypeAlias = JsonData | str | bytes


class BaseHTTPClient:
    def __init__(
        self,
        base_url: str = "",
        timeout: int = Default.TIMEOUT,
        headers: Optional[Headers] = None,
    ):
        self._base_url = base_url
        self._headers = headers or {}
        self._timeout = aiohttp.ClientTimeout(timeout)
        self._ratelimit: Optional[RateLimit] = None

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ) -> Any:
        url = urljoin(self._base_url + "/", endpoint.lstrip("/"))

        rparams = params.to_dict() if isinstance(params, Params) else {}
        rheaders = {**self._headers, **(headers or {})}

        async with aiohttp.ClientSession(timeout=self._timeout) as session:
            async with session.request(
                method=method,
                url=url,
                params=rparams,
                headers=rheaders,
                data=data,
            ) as response:
                return await self._handle(response)

    async def _handle(self, response: aiohttp.ClientResponse) -> Any:
        await self._update_ratelimit(response)

        if not (200 <= response.status < 300):
            await self._onerror(response)

        content_type = response.headers.get("content-type", "").lower()

        if "application/json" in content_type:
            return await response.json()

        return await response.text()

    async def _update_ratelimit(self, response: aiohttp.ClientResponse):
        try:
            self._ratelimit = RateLimit.model_validate(response.headers)

        except ValidationError:
            pass

    async def _onerror(self, response: aiohttp.ClientResponse) -> None:
        try:
            data = await response.json()
            msg = data.get("error", data.get("message"))

        except Exception:
            msg = await response.text()

        msg = msg or f"HTTP {response.status}"

        # TODO: CUSTOM EXCEPTION
        raise Exception(msg)
