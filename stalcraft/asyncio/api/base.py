from typing import Any, Optional
from pathlib import Path

import httpx

from stalcraft.api.base import BaseApi


class AsyncBaseApi(BaseApi):
    async def request_get(self, url: Path, params: Optional[httpx.QueryParams] = None) -> Any:
        async with httpx.AsyncClient(**self._httpx_config) as client:
            response = await client.get(url=url.as_posix(), params=params, headers=self.headers)

        return self._parse_response(response)
