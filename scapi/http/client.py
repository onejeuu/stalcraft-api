from typing import Optional

from .base import BaseHTTPClient, Data, Headers, Params


class HTTPClient(BaseHTTPClient):
    async def GET(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
    ):
        return await self._request(
            "GET",
            url=url,
            params=params,
            headers=headers,
        )

    async def POST(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ):
        return await self._request(
            "POST",
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    async def PUT(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ):
        return await self._request(
            "PUT",
            url=url,
            params=params,
            data=data,
            headers=headers,
        )

    async def DELETE(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
    ):
        return await self._request(
            "DELETE",
            url=url,
            params=params,
            headers=headers,
        )

    async def PATCH(
        self,
        url: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ):
        return await self._request(
            "PATCH",
            url=url,
            params=params,
            data=data,
            headers=headers,
        )
