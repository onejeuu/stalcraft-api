from typing import Optional

from .base import BaseHTTPClient, Data, Headers, Params


class HTTPClient(BaseHTTPClient):
    async def GET(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[int] = None,
        filename: Optional[str] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="GET",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            filename=filename,
            raw=raw,
        )

    async def POST(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        timeout: Optional[int] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            raw=raw,
        )

    async def PUT(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        timeout: Optional[int] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            raw=raw,
        )

    async def DELETE(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        timeout: Optional[int] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="DELETE",
            url=url,
            params=params,
            headers=headers,
            timeout=timeout,
            raw=raw,
        )

    async def PATCH(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
        timeout: Optional[int] = None,
        raw: bool = False,
    ):
        return await self._request(
            method="PATCH",
            url=url,
            params=params,
            data=data,
            headers=headers,
            timeout=timeout,
            raw=raw,
        )
