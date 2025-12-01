from scapi.client import models

from .shared import ClanEndpoint


class UserClanEndpoint(ClanEndpoint):
    """Endpoint for user specific clan operations."""

    async def members(
        self,
    ) -> list[models.ClanMember]:
        """
        Retrieve clan member list.

        **WARN:** Requires user clan membership.

        Returns:
            List of clan members with ranks and join times.
        """

        response = await self._http.GET(
            url=f"{self._region}/clan/{self._clan_id}/members",
        )

        return self._parse(response, models.ClanMember)
