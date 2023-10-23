from typing import Any, List, Optional

from stalcraft import Region, UserClan
from stalcraft import exceptions as exc
from stalcraft import schemas
from stalcraft.default import Default
from stalcraft.client.base import BaseClient
from stalcraft.utils import Method


class UserClient(BaseClient):
    def __init__(
        self,
        token: Optional[str] = None,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        """
        User Client for working with the API.

        Args:
            token: User access token.
            base_url (optional): API base url. Defaults to PRODUCTION.
            json (optional): if True response returned in raw format. Defaults to False.
        """

        self._token = token

        super().__init__(base_url, json)

    def _get_api(self):
        if self._token:
            return self._TOKEN_API(self._token, self._base_url)

        raise exc.MissingCredentials("No token provided.")

    def clan(
        self,
        clan_id: str,
        region: Region = Default.REGION
    ) -> UserClan:
        """
        Factory method for working with clans.

        Args:
            clan_id: Clan ID. For example "647d6c53-b3d7-4d30-8d08-de874eb1d845".
            region: Stalcraft server region.
        """

        return UserClan(self._api, clan_id, region, self.json)

    def characters(
        self,
        region: Region = Default.REGION
    ) -> Any | List[schemas.Character]:
        """
        Returns list of characters created by the user by which used access token was provided.

        Args:
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Method(region, "characters")
        )

        return response if self.json else [schemas.Character.parse_obj(character) for character in response]

    def friends(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | List[str]:
        """
        Returns list of character names who are friend with specified character.

        Args:
            character: Character name.
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Method(region, "friends", character)
        )

        return response
