from typing import Optional

from scapi.consts import BaseUrl
from scapi.defaults import Default
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params

from . import models


class OAuthClient(APIClient):
    """Client for OAuth 2.0 authentication with EXBO services."""

    def __init__(
        self,
        *,
        client_id: str,
        client_secret: str,
        base_url: str = BaseUrl.OAUTH,
        redirect_uri: str = Default.REDIRECT_URI,
        scope: str = Default.SCOPE,
        json: bool = Default.JSON,
    ):
        """
        Initialize OAuth client with application credentials.

        Args:
            client_id: Application client identifier.
            client_secret: Application client secret.
            base_url (optional): OAuth server base URL.
            redirect_uri (optional): Redirect URI for authorization flow.
            scope (optional, stub): Requested access scope.
            json (optional): Return raw JSON instead of validated models.
        """

        self._client_id = client_id
        self._client_secret = client_secret
        self._base_url = base_url
        self._redirect_uri = redirect_uri
        self._scope = scope
        self._json = json

        self._http = HTTPClient(base_url=base_url)

    def get_authorize_url(
        self,
        state: Optional[str] = None,
        redirect_uri: Optional[str] = None,
        scope: Optional[str] = None,
    ) -> str:
        """
        Generate user authorization URL.

        Args:
            state (optional): CSRF protection state string.
            redirect_uri (optional): Override default redirect URI.
            scope (optional): Override default scope.

        Returns:
            URL for user authorization.
        """

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
        """
        Request application token using client credentials grant.

        **Note:** New tokens replace and invalidate previous ones.

        Args:
            scope (optional): Override default scope.

        Returns:
            Application token data.
        """

        response = await self._http.POST(
            url="token",
            data={
                "client_id": self._client_id,
                "client_secret": self._client_secret,
                "scope": scope or self._scope,
                "grant_type": "client_credentials",
            },
        )

        return self._parse(response, models.AppToken)

    async def get_user_token(
        self,
        code: str,
    ) -> models.UserToken:
        """
        Exchange authorization code for user token.

        **Note:** New tokens replace and invalidate previous ones.

        Args:
            code: Authorization code from user redirect.

        Returns:
            User token data with access and refresh token.
        """

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

        return self._parse(response, models.UserToken)

    async def refresh_user_token(
        self,
        refresh_token: str,
        scope: Optional[str] = None,
    ) -> models.UserToken:
        """
        Refresh expired user access token.

        Args:
            refresh_token: Refresh token from previous authorization.
            scope (optional): Override default scope.

        Returns:
            Refreshed user token data.
        """

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

        return self._parse(response, models.UserToken)

    async def validate_user_token(
        self,
        token: str,
    ) -> models.UserInfo:
        """
        Validate user token and retrieve user information.

        Args:
            token: User access token.

        Returns:
            User account information.
        """

        response = await self._http.GET(
            url="user",
            headers={"Authorization": f"Bearer {token}"},
        )

        return self._parse(response, models.UserInfo)
