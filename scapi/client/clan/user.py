from scapi.client import models

from .shared import ClanEndpoint


class UserClanEndpoint(ClanEndpoint):
    async def members(
        self,
    ) -> list[models.ClanMember]:
        response = await self._http.GET(
            url=f"{self._region}/clan/{self._clan_id}/members",
        )

        return [models.ClanMember.model_validate(member) for member in response]
