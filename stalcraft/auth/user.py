from typing import Any

from stalcraft import schemas
from stalcraft.auth.base import BaseAuth
from stalcraft.consts import AuthUrl
from stalcraft.default import Default
from stalcraft.utils import Params


class UserAuth(BaseAuth):
    @property
    def code_url(self, response_type: str = Default.RESPONSE_TYPE) -> str:
        """
        Returns the URL that a user should visit to authorize the application.
        """

        params = Params(
            client_id = self._client_id,
            redirect_uri = self.redirect_uri,
            scope = self.scope,
            response_type = response_type
        )

        return f"{AuthUrl.AUTHORIZE}?{params}"

    def get_token(self, code: str) -> Any | schemas.UserToken:
        """
        Returns an OAuth2 token for the user, using the authorization code.

        Args:
            code: Authorization code acquired after user authorized in your app by "code_url".
        """

        response = self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": self.redirect_uri
            }
        )

        return response if self.json else schemas.UserToken.parse_obj(response)

    def refresh_token(self, refresh_token: str) -> Any | schemas.UserToken:
        """
        Returns a new OAuth2 token using a refresh token.

        Args:
            refresh_token: The refresh token to use.
        """

        response = self._request_post(
            url=AuthUrl.TOKEN,
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "scope": self.scope
            }
        )

        return response if self.json else schemas.UserToken.parse_obj(response)

    def token_info(self, token: str) -> Any | schemas.TokenInfo:
        """
        Returns user information associated with the provided access token.

        Args:
            token: User access token.
        """

        response = self._request_get(
            url=AuthUrl.USER,
            headers={
                "Authorization": f"Bearer {token}"
            }
        )

        return response if self.json else schemas.TokenInfo.parse_obj(response)
