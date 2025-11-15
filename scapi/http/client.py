from typing import Any, Optional
from .base import BaseHTTPClient, Params, Headers, Data


class HTTPClient(BaseHTTPClient):
    async def GET(
        self,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
    ) -> Any:
        return await self._request(
            "GET",
            endpoint,
            params=params,
            headers=headers,
        )

    async def POST(
        self,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ) -> Any:
        return await self._request(
            "POST",
            endpoint,
            params=params,
            data=data,
            headers=headers,
        )

    async def PUT(
        self,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ) -> Any:
        return await self._request(
            "PUT",
            endpoint,
            params=params,
            data=data,
            headers=headers,
        )

    async def DELETE(
        self,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
    ) -> Any:
        return await self._request(
            "DELETE",
            endpoint,
            params=params,
            headers=headers,
        )

    async def PATCH(
        self,
        endpoint: str,
        params: Optional[Params] = None,
        headers: Optional[Headers] = None,
        data: Optional[Data] = None,
    ) -> Any:
        return await self._request(
            "PATCH",
            endpoint,
            params=params,
            data=data,
            headers=headers,
        )
