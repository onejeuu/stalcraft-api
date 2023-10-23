from typing import Any, Dict

import httpx

from stalcraft.api.base import validate_status_code
from stalcraft.auth.base import BaseAuth


class AsyncBaseAuth(BaseAuth):
    async def _request_get(self, url: str, headers: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.get(url=url, headers=headers)

        validate_status_code(response)

        return response.json()

    async def _request_post(self, url: str, data: Dict[str, Any]) -> Any:
        async with httpx.AsyncClient() as client:
            response = await client.post(url=url, data=data)

        validate_status_code(response)

        return response.json()
