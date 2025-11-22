from typing import Optional

from scapi.consts import BaseUrl
from scapi.defaults import Default
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params

from . import models


class OAuthClient(APIClient):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        base_url: str = BaseUrl.OAUTH,
        scope: str = Default.SCOPE,
        redirect_uri: str = Default.REDIRECT_URI,
    ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._scope = scope
        self._redirect_uri = redirect_uri

        self._http = HTTPClient(base_url=base_url)

    def get_authorize_url(
        self,
        scope: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        state: Optional[str] = None,
    ) -> str:
        params = Params(
            client_id=self._client_id,
            redirect_uri=redirect_uri or self._redirect_uri,
            scope=scope or self._scope,
            state=state,
            response_type="code",
        )

        return f"{self._base_url}/authorize?{params}"

    async def get_app_token(
        self,
        scope: Optional[str] = None,
    ) -> models.AppToken:
        response = await self._http.POST(
            url="token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": scope or self._scope,
                "grant_type": "client_credentials",
            },
        )

        return models.AppToken.model_validate(response)

    async def get_user_token(
        self,
        code: str,
    ) -> models.UserToken:
        response = await self._http.POST(
            url="token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "redirect_uri": self._redirect_uri,
                "grant_type": "authorization_code",
            },
        )

        return models.UserToken.model_validate(response)

    async def refresh_user_token(
        self,
        refresh_token: str,
        scope: Optional[str] = None,
    ) -> models.UserToken:
        response = await self._http.POST(
            url="token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "refresh_token": refresh_token,
                "scope": scope or self._scope,
                "grant_type": "refresh_token",
            },
        )

        return models.UserToken.model_validate(response)

    async def validate_user_token(
        self,
        token: str,
    ) -> models.UserInfo:
        response = await self._http.GET(
            url="user",
            headers={"Authorization": f"Bearer {token}"},
        )

        return models.UserInfo.model_validate(response)
