from typing import Optional

from scapi.client import models
from scapi.config import Config
from scapi.enums import Region

from .shared import ClanEndpoint


class UserClanEndpoint(ClanEndpoint):
    """User specific clan endpoint for specified clan."""

    async def members(
        self,
        region: Optional[str | Region] = None,
    ) -> list[models.ClanMember]:
        """
        Retrieve clan member list.

        **WARN:** Requires user clan membership.

        Args:
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            List of clan members with ranks and join times.
        """

        region = (region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/clan/{self._clan_id}/members",
        )

        return self._parse(response, models.ClanMember)
