from typing import Any

from stalcraft import schemas
from stalcraft.asyncio.auth.base import AsyncBaseAuth
from stalcraft.auth import AppAuth
from stalcraft.consts import AuthUrl


class AsyncAppAuth(AsyncBaseAuth, AppAuth):
    async def get_token(self) -> Any | schemas.AppToken:
        response = await self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
                "scope": self.scope
            }
        )

        return response if self.json else schemas.AppToken.parse_obj(response)
