from typing import Any

from stalcraft import schemas
from stalcraft.clan import Clan
from stalcraft.utils import Method


class UserClan(Clan):
    def members(self) -> Any | list[schemas.ClanMember]:
        """
        Returns list of members in the given clan.

        ! Can be used ONLY when using user access token and that user has at least one character in that clan.
        """

        response = self._api.request_get(
            Method(self.region, "clan", self.clan_id, "members")
        )

        return response if self.json else [schemas.ClanMember.parse_obj(member) for member in response]
