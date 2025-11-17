from typing import Any, Dict, Optional, TypeAlias
from urllib.parse import urljoin

import aiofiles
from aiohttp import ClientResponse, ClientSession, ClientTimeout
from pydantic import ValidationError

from scapi.defaults import Default

from .params import Params
from .ratelimit import RateLimit


Headers: TypeAlias = Dict[str, str]

JsonData: TypeAlias = Dict[str, Any]
Data: TypeAlias = JsonData | str | bytes


CHUNK_SIZE = 1024 * 8


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
        filename: Optional[str] = None,
        raw: bool = False,
    ) -> Any:
        url = urljoin(self._base_url + "/", url.lstrip("/"))

        # Prepare request options
        rtimeout = ClientTimeout(timeout) if timeout else self._timeout
        rparams = params.to_dict() if isinstance(params, Params) else {}
        rheaders = {**self._headers, **(headers or {})}

        # Create session and send request
        async with ClientSession(timeout=rtimeout) as session:
            async with session.request(method=method, url=url, params=rparams, headers=rheaders, data=data) as response:
                # Update ratelimit headers
                await self._update_ratelimit(response)

                # Validate status code
                if not (200 <= response.status < 300):
                    await self._on_error(response)

                # Stream data to file path
                if filename:
                    return await self._stream_to_file(response, filename)

                # Parse response by content type
                try:
                    data = await self._parse(response, raw)

                finally:
                    await response.release()

                return data

    async def _parse(self, response: ClientResponse, raw: bool) -> Any:
        if not raw:
            content_type = response.headers.get("content-type", "").lower()

            if "application/json" in content_type:
                return await response.json()

            if content_type.startswith("text/") or "xml" in content_type:
                return await response.text()

        return await response.read()

    async def _stream_to_file(self, response: ClientResponse, filename: str) -> str:
        async with aiofiles.open(filename, "wb") as f:
            # Download file by chunks
            async for chunk in response.content.iter_chunked(CHUNK_SIZE):
                await f.write(chunk)
        return filename

    async def _update_ratelimit(self, response: ClientResponse) -> None:
        try:
            self._ratelimit = RateLimit.model_validate(response.headers)

        except ValidationError:
            pass

    async def _on_error(self, response: ClientResponse) -> None:
        try:
            data = await response.json()
            msg = data.get("error", data.get("message"))

        except Exception:
            msg = await response.text()

        msg = msg or f"HTTP {response.status}"

        # TODO: CUSTOM EXCEPTION
        raise Exception(msg)
