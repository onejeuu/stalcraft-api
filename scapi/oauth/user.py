from scapi import models
from scapi.consts import OAuthUrl
from scapi.defaults import Default
from scapi.http.params import Params

from .base import BaseOAuth


class UserOAuth(BaseOAuth):
    @property
    def code_url(
        self,
        response_type: str = Default.RESPONSE_TYPE,
        endpoint: str = OAuthUrl.AUTHORIZE,
    ) -> str:
        params = Params(
            client_id=self._client_id,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            response_type=response_type,
        )

        return f"{endpoint}?{params}"

    async def get_token(
        self,
        code: str,
        endpoint: str = OAuthUrl.TOKEN,
    ) -> models.oauth.UserToken:
        response = await self._http.POST(
            endpoint=endpoint,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "redirect_uri": self.redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        return models.oauth.UserToken.model_validate(response)

    async def refresh_token(
        self,
        refresh_token: str,
        endpoint: str = OAuthUrl.TOKEN,
    ) -> models.oauth.UserToken:
        response = await self._http.POST(
            endpoint=endpoint,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": refresh_token,
                "scope": self.scope,
                "grant_type": "refresh_token",
            },
        )

        return models.oauth.UserToken.model_validate(response)

    # TODO: RENAME ME!
    async def token_info(
        self,
        token: str,
        endpoint: str = OAuthUrl.USER,
    ) -> models.oauth.TokenInfo:
        response = await self._http.GET(
            endpoint=endpoint,
            headers={"Authorization": f"Bearer {token}"},
        )

        return models.oauth.TokenInfo.model_validate(response)
