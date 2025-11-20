from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from scapi.client import models
from scapi.client.types import Listing
from scapi.defaults import Default
from scapi.enums import Order, Region, SortOperation
from scapi.http.client import HTTPClient
from scapi.http.params import Params

from .auction.shared import Auction


class BaseClient(ABC):
    def __init__(
        self,
        base_url: str = Default.BASE_URL,
    ):
        self._base_url = base_url

        self._http = self._create_http_client()

    @abstractmethod
    def _create_http_client(self) -> HTTPClient:
        pass

    async def regions(
        self,
    ) -> list[models.RegionInfo]:
        response = await self._http.GET(
            url="regions",
        )

        return [models.RegionInfo.model_validate(region) for region in response]

    async def emission(
        self,
        region: Region = Default.REGION,
    ) -> models.Emission:
        response = await self._http.GET(
            url=f"{region}/emission",
        )

        return models.Emission.model_validate(response)

    async def character_profile(
        self,
        username: str,
        region: Region = Default.REGION,
    ) -> models.CharacterProfile:
        response = await self._http.GET(
            url=f"{region}/character/by-name/{username}/profile",
        )

        return models.CharacterProfile.model_validate(response)

    async def clans(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        region: Region = Default.REGION,
    ) -> Listing[models.ClanInfo]:
        response = await self._http.GET(
            url=f"{region}/clans",
            params=Params(limit=limit, offset=offset),
        )

        return Listing(response, models.ClanInfo, "data", "totalClans")

    async def operations(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: SortOperation = Default.SORT_OPERATION,
        order: Order = Default.ORDER,
        map: Optional[str] = None,
        username: Optional[str] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        region: Region = Default.REGION,
    ) -> Listing[models.OperationSession]:
        response = await self._http.GET(
            url=f"{region}/operations/sessions",
            params=Params(
                limit=limit,
                offset=offset,
                sort=sort,
                order=order,
                map=map,
                username=username,
                before=before.strftime("%Y-%m-%dT%H:%M:%SZ") if before else None,
                after=after.strftime("%Y-%m-%dT%H:%M:%SZ") if after else None,
            ),
        )

        return Listing(response, models.OperationSession, "sessions", "total")

    def auction(
        self,
        item_id: str,
        region: Region = Default.REGION,
    ) -> Auction:
        return Auction(self._http, item_id, region)
