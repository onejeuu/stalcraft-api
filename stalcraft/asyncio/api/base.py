from typing import Any

import httpx

from stalcraft.api.base import BaseApi, RequestParams, validate_status_code
from stalcraft.utils import Method, Params


class AsyncBaseApi(BaseApi):
    async def request_get(self, method: str | Method, params: RequestParams | Params={}) -> Any:
        method, params = self._parse_request_args(method, params)

        async with httpx.AsyncClient(base_url=self._base_url, timeout=self._timeout) as client:
            response = await client.get(url=method, params=params, headers=self.headers)

        validate_status_code(response)
        self._update_rate_limit(response.headers)

        return response.json()
