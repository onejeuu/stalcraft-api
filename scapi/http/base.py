from typing import Any, Dict, Optional, TypeAlias
from urllib.parse import urljoin

from aiohttp import ClientResponse, ClientSession, ClientTimeout
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
        self._timeout = ClientTimeout(timeout)
        self._ratelimit: Optional[RateLimit] = None

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        timeout: Optional[int] = None,
    ) -> Any:
        url = urljoin(self._base_url + "/", url.lstrip("/"))

        rtimeout = ClientTimeout(timeout) if timeout else self._timeout
        rparams = params.to_dict() if isinstance(params, Params) else {}
        rheaders = {**self._headers, **(headers or {})}

        async with ClientSession(timeout=rtimeout) as session:
            response = await session.request(
                method=method,
                url=url,
                params=rparams,
                headers=rheaders,
                data=data,
            )
            return await self._handle(response)

    async def _handle(self, response: ClientResponse) -> Any:
        await self._update_ratelimit(response)

        if not (200 <= response.status < 300):
            await self._onerror(response)

        return await self._parse(response)

    async def _parse(self, response: ClientResponse) -> Any:
        content_type = response.headers.get("content-type", "").lower()

        try:
            if "application/json" in content_type:
                return await response.json()

            if content_type.startswith("text/") or "xml" in content_type:
                return await response.text()

            return await response.read()

        finally:
            await response.release()

    async def _update_ratelimit(self, response: ClientResponse) -> None:
        try:
            self._ratelimit = RateLimit.model_validate(response.headers)

        except ValidationError:
            pass

    async def _onerror(self, response: ClientResponse) -> None:
        try:
            data = await response.json()
            msg = data.get("error", data.get("message"))

        except Exception:
            msg = await response.text()

        msg = msg or f"HTTP {response.status}"

        # TODO: CUSTOM EXCEPTION
        raise Exception(msg)
