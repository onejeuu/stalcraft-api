import asyncio
import atexit
import socket
from types import TracebackType
from typing import Any, Dict, Optional, TypeAlias
from urllib.parse import urljoin

import aiofiles
from aiohttp import ClientResponse, ClientSession, ClientTimeout, TCPConnector
from pydantic import ValidationError

from scapi import exceptions
from scapi.defaults import Default

from .params import Params
from .ratelimit import RateLimit


Headers: TypeAlias = Dict[str, str]
Json: TypeAlias = Dict[str, Any]
Data: TypeAlias = Json | str | bytes


class HTTPClient:
    TTL_DNS_CACHE = 60
    STREAM_CHUNK_SIZE = 1024 * 8

    def __init__(
        self,
        base_url: str = "",
        timeout: int = Default.TIMEOUT,
        headers: Optional[Headers] = None,
    ):
        self._base_url = base_url.rstrip("/")
        self._timeout = timeout
        self._headers = headers or {}

        self._session: Optional[ClientSession] = None
        self._ratelimit: Optional[RateLimit] = None

        atexit.register(self._cleanup)

    async def _create_session(self) -> ClientSession:
        if self._session is None:
            self._session = ClientSession(
                timeout=ClientTimeout(total=self._timeout),
                connector=TCPConnector(
                    family=socket.AF_INET,
                    ttl_dns_cache=self.TTL_DNS_CACHE,
                    force_close=True,
                ),
            )
        return self._session

    async def _request(
        self,
        method: str,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        filename: Optional[str] = None,
        raw: bool = False,
    ) -> Any:
        url = urljoin(self._base_url + "/", url.lstrip("/"))

        # Prepare request options
        rparams = params.to_dict() if isinstance(params, Params) else {}
        rheaders = {**self._headers, **(headers or {})}

        # Create session
        session = await self._create_session()

        # Send http request
        async with session.request(method=method, url=url, params=rparams, headers=rheaders, data=data) as response:
            # Update ratelimit by response headers
            await self._update_ratelimit(response)

            # Validate response status code
            if not (200 <= response.status < 300):
                await self._on_error(response)

            # Stream response data to file path
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
        async with aiofiles.open(filename, "wb") as fp:
            async for chunk in response.content.iter_chunked(self.STREAM_CHUNK_SIZE):
                await fp.write(chunk)
        return filename

    async def _update_ratelimit(self, response: ClientResponse) -> None:
        try:
            self._ratelimit = RateLimit.model_validate(response.headers)

        except ValidationError:
            pass

    async def _on_error(self, response: ClientResponse) -> None:
        # TODO: status code exceptions mapping & error trim (on large response)

        default = "Unknown error"

        try:
            error = await response.json()

        except Exception:
            error = {"error": await response.text(errors="replace") or default}

        raise exceptions.RequestError(error, response.status, response.method, response.url)

    async def GET(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        filename: Optional[str] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            filename=filename,
            raw=raw,
        )

    async def POST(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
            raw=raw,
        )

    async def PUT(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
            raw=raw,
        )

    async def DELETE(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
            raw=raw,
        )

    async def PATCH(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="PATCH",
            url=url,
            params=params,
            data=data,
            headers=headers,
            raw=raw,
        )

    def _cleanup(self) -> None:
        if self._session and not self._session.closed:
            try:
                loop = asyncio.new_event_loop()
                loop.run_until_complete(self._session.close())
                loop.close()
            except Exception:
                pass

    async def close(self) -> None:
        if self._session and not self._session.closed:
            await self._session.close()

    async def __aenter__(self):
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ):
        await self.close()
        return False

    def __str__(self):
        return f"<{self.__class__.__name__} base_url='{self._base_url}' timeout={self._timeout} ratelimit={repr(self._ratelimit)}>"
