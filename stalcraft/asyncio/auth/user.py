from typing import Any

from stalcraft import schemas
from stalcraft.asyncio.auth.base import AsyncBaseAuth
from stalcraft.auth import UserAuth
from stalcraft.consts import AuthUrl


class AsyncUserAuth(AsyncBaseAuth, UserAuth):
    async def get_token(self, code: str) -> Any | schemas.UserToken:
        response = await self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }
        )

        return response if self.json else schemas.UserToken.model_validate(response)

    async def refresh_token(self, refresh_token: str) -> Any | schemas.UserToken:
        response = await self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": self.scope
            }
        )

        return response if self.json else schemas.UserToken.model_validate(response)

    async def token_info(self, token: str) -> Any | schemas.TokenInfo:
        response = await self._request_get(
            url=AuthUrl.USER,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        return response if self.json else schemas.TokenInfo.model_validate(response)
