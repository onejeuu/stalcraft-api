import requests

from . import schemas


class Authorization:
    AUTHORIZE_URL = "https://exbo.net/oauth/authorize"
    TOKEN_URL = "https://exbo.net/oauth/token"
    USER_URL = "https://exbo.net/oauth/user"

    def __init__(self, client_id: str, client_secret: str, scope="", redirect_uri="http://localhost", json=True):
        """
        Constructor for Authorization.

        Args:
            client_id: OAuth2 client ID
            client_secret: OAuth2 client secret
            scope (optional): Authorization scope requested by the client. Defaults to ""
            redirect_uri (optional): URI to redirect the user to after authorization. Defaults to "http://localhost"
            json (optional): if True response returned in raw format. Defaults to True
        """

        self.client_id = client_id
        self.client_secret = client_secret
        self.scope = scope
        self.redirect_uri = redirect_uri
        self.json = json

        self.code = ""

    @property
    def user_code_url(self):
        """
        Returns the URL that a user should visit to authorize the application.
        """

        return f"{self.AUTHORIZE_URL}?client_id={self.client_id}&redirect_uri={self.redirect_uri}&scope={self.scope}&response_type=code"

    def input_code(self):
        """
        Allows the developer to input the authorization code from the redirect URL via the console.
        """

        self.code = input("Enter the authorization code from the redirect URL: ")

    def get_user_token(self):
        """
        Returns an OAuth2 token for the user, using the authorization code.
        """

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "code": self.code,
            "grant_type": "authorization_code",
            "redirect_uri": self.redirect_uri
        }

        response = requests.post(self.TOKEN_URL, data=data).json()

        if self.json is True:
            return response

        return schemas.UserToken.parse_obj(response)

    def get_app_token(self):
        """
        Returns an OAuth2 token for the application, using the client credentials.
        """

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials",
            "scope": self.scope
        }

        response = requests.post(self.TOKEN_URL, data=data).json()

        if self.json is True:
            return response

        return schemas.AppToken.parse_obj(response)

    def update_token(self, refresh_token: str):
        """
        Returns a new OAuth2 token using a refresh token.

        Args:
            refresh_token: The refresh token to use
        """

        data = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "refresh_token",
            "refresh_token": refresh_token,
            "scope": self.scope
        }

        response = requests.post(self.TOKEN_URL, data=data)

        if self.json is True:
            return response

        return schemas.UserToken.parse_obj(response)

    def info(self, token: str):
        """
        Returns user information associated with the provided access token.

        Args:
            token: User access token
        """

        headers = {
            "Authorization": f"Bearer {token}"
        }

        response = requests.get(self.USER_URL, headers=headers).json()

        if self.json is True:
            return response

        return schemas.TokenInfo.parse_obj(response)

    def __str__(self):
        return f"<{self.__class__.__name__}> client_id='{self.client_id}' redirect_uri='{self.redirect_uri}'"
