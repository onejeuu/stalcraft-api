from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from scapi.client import models
from scapi.defaults import Default
from scapi.enums import OperationsMap, Order, Region, SortAuction
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.http.types import Listing

from .auction.shared import AuctionEndpoint


class SharedClient(ABC, APIClient):
    def __init__(
        self,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON,
    ):
        self._base_url = base_url
        self._json = json
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

        return self._parse(response, models.RegionInfo)

    async def emission(
        self,
        region: str | Region = Default.REGION,
    ) -> models.Emission:
        response = await self._http.GET(
            url=f"{region}/emission",
        )

        return self._parse(response, models.Emission)

    async def character_profile(
        self,
        username: str,
        region: str | Region = Default.REGION,
    ) -> models.CharacterProfile:
        response = await self._http.GET(
            url=f"{region}/character/by-name/{username}/profile",
        )

        return self._parse(response, models.CharacterProfile)

    async def clans(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        region: str | Region = Default.REGION,
    ) -> Listing[models.ClanInfo]:
        response = await self._http.GET(
            url=f"{region}/clans",
            params=Params(limit=limit, offset=offset),
        )

        return self._parse(response, models.ClanInfo, ("data", "totalClans"))

    async def operations(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: str | SortAuction = Default.SORT_OPERATION,
        order: str | Order = Default.ORDER,
        map: Optional[str | OperationsMap] = None,
        username: Optional[str] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        region: str | Region = Default.REGION,
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

        return self._parse(response, models.OperationSession, ("sessions", "total"))

    def auction(
        self,
        item_id: str,
        region: str | Region = Default.REGION,
    ) -> AuctionEndpoint:
        return AuctionEndpoint(self._http, item_id, region, self._json)
