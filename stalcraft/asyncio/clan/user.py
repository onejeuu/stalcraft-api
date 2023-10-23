from typing import Any

from stalcraft import schemas
from stalcraft.asyncio.clan.clan import AsyncClan
from stalcraft.clan.user import UserClan
from stalcraft.utils import Method


class AsyncUserClan(AsyncClan, UserClan):
    async def members(self) -> Any | list[schemas.ClanMember]:
        response = await self._api.request_get(
            Method(self.region, "clan", self.clan_id, "members")
        )

        return response if self.json else [schemas.ClanMember.parse_obj(member) for member in response]
