from pathlib import Path
from typing import Any

from stalcraft import schemas
from stalcraft.asyncio.clan.clan import AsyncClan
from stalcraft.clan.user import UserClan


class AsyncUserClan(AsyncClan, UserClan):
    async def members(self) -> Any | list[schemas.ClanMember]:
        response = await self._api.request_get(
            Path(self.region, "clan", self.clan_id, "members")
        )

        return response if self.json else [schemas.ClanMember.model_validate(member) for member in response]
