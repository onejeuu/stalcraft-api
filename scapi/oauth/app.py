from scapi import models
from scapi.consts import OAuthUrl

from .base import BaseOAuth


class AppOAuth(BaseOAuth):
    async def get_token(
        self,
        endpoint: str = OAuthUrl.TOKEN,
    ) -> models.oauth.AppToken:
        response = await self._http.POST(
            endpoint=endpoint,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": self.scope,
                "grant_type": "client_credentials",
            },
        )

        return models.oauth.AppToken.model_validate(response)
