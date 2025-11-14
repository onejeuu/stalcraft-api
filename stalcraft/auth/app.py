from typing import Any

from stalcraft import schemas
from stalcraft.auth.base import BaseAuth
from stalcraft.consts import AuthUrl


class AppAuth(BaseAuth):
    def get_token(self) -> Any | schemas.AppToken:
        """
        Returns an OAuth2 token for the application, using the client credentials.
        """

        response = self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "client_credentials",
                "scope": self.scope
            }
        )

        return response if self.json else schemas.AppToken.model_validate(response)
