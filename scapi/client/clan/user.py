from scapi import models

from .shared import Clan


class UserClan(Clan):
    async def members(
        self,
    ) -> list[models.api.ClanMember]:
        response = await self._http.GET(
            url=f"{self.region}/clan/{self.clan_id}/members",
        )

        return [models.api.ClanMember.model_validate(member) for member in response]
