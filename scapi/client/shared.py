from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from scapi.client import models
from scapi.config import Config
from scapi.consts import BaseUrl, Defaults
from scapi.enums import OperationsMap, Order, Region, SortOperations
from scapi.http.api import APIClient
from scapi.http.client import HTTPClient
from scapi.http.params import Params
from scapi.http.types import Listing

from .auction.shared import AuctionEndpoint


class SharedClient(ABC, APIClient):
    """Base API client for shared endpoints."""

    def __init__(
        self,
        *,
        base_url: str = BaseUrl.PRODUCTION,
        json: bool = Defaults.JSON,
        region: Optional[Region | str] = None,
    ):
        """
        Initialize shared client.

        Args:
            base_url (optional): API server base URL. Defaults to `http://eapi.stalcraft.net`.
            json (optional): Return JSON instead of models. Defaults to `False`.
            region (optional): Default game server region. Defaults to `ru`.
        """

        self._base_url = base_url
        self._json = json
        self._region = region
        self._http = self._create_http_client()

    @abstractmethod
    def _create_http_client(self) -> HTTPClient:
        """Create HTTP client with appropriate authentication."""
        pass

    async def regions(
        self,
    ) -> list[models.RegionInfo]:
        """
        Retrieve available game server regions.

        Returns:
            List of regions.
        """

        response = await self._http.GET(
            url="regions",
        )

        return self._parse(response, models.RegionInfo)

    async def emission(
        self,
        region: Optional[Region | str] = None,
    ) -> models.EmissionState:
        """
        Get current emission state.

        Args:
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Emission state.
        """

        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/emission",
        )

        return self._parse(response, models.EmissionState)

    async def profile(
        self,
        username: str,
        region: Optional[Region | str] = None,
    ) -> models.CharacterProfile:
        """
        Retrieve public character profile including alliance, stats, and clan affiliation.

        Args:
            username: Character name.
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Public character profile data.
        """

        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/character/by-name/{username}/profile",
        )

        return self._parse(response, models.CharacterProfile)

    async def clans(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        region: Optional[Region | str] = None,
    ) -> Listing[models.ClanInfo]:
        """
        List all registered clans.

        Args:
            limit (optional): Amount of clans to return, starting from offset, (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of clans to skip. Defaults to `0`.
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Paginated clan listing.
        """

        limit = max(0, min(200, limit or Config.LIMIT))
        offset = max(0, offset or Config.OFFSET)
        region = (region or self._region or Config.REGION).lower()

        response = await self._http.GET(
            url=f"{region}/clans",
            params=Params(limit=limit, offset=offset),
        )

        return self._parse(response, models.ClanInfo, ("data", "totalClans"))

    async def operations_sessions(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
        sort: Optional[SortOperations | str] = None,
        order: Optional[Order | str] = None,
        map: Optional[OperationsMap | str] = None,
        username: Optional[str] = None,
        before: Optional[datetime | str] = None,
        after: Optional[datetime | str] = None,
        region: Optional[Region | str] = None,
    ) -> Listing[models.OperationSession]:
        """
        Returns list of operation sessions.

        Args:
            limit (optional): Amount of sessions to return, starting from offset, (`0`-`100`). Defaults to `20`.
            offset (optional): Amount of sessions to skip. Defaults to `0`.
            sort (optional): Sorting field. Defaults to `date_finish`.
            order (optional): Sorting direction. Defaults to `ascending`.
            map (optional): Filter by operations map name.
            username (optional): Filter by character name.
            before (optional): Filter sessions finished before ISO date (`%Y-%m-%dT%H:%M:%SZ`).
            after (optional): Filter sessions finished after ISO date (`%Y-%m-%dT%H:%M:%SZ`).
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Paginated operations sessions listing.
        """

        limit = max(0, min(100, limit or Config.LIMIT))
        offset = max(0, offset or Config.OFFSET)
        sort = (sort or Config.SORT_OPERATION).lower()
        order = (order or Config.ORDER).lower()
        map = map.lower() if map else None
        region = (region or self._region or Config.REGION).lower()

        def _format_date(value: Optional[datetime | str]):
            if value and isinstance(value, datetime):
                return value.strftime("%Y-%m-%dT%H:%M:%SZ")

            if value and isinstance(value, str):
                try:
                    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
                    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

                except ValueError:
                    return value

            return value

        before = _format_date(before)
        after = _format_date(after)

        response = await self._http.GET(
            url=f"{region}/operations/sessions",
            params=Params(
                limit=limit,
                offset=offset,
                sort=sort,
                order=order,
                map=map,
                username=username,
                before=before,
                after=after,
            ),
        )

        return self._parse(response, models.OperationSession, ("sessions", "total"))

    def auction(
        self,
        item_id: str,
        region: Optional[Region | str] = None,
    ) -> AuctionEndpoint:
        """
        Factory method for auction endpoint.

        Args:
            item_id: Item identifier.
            region (optional): Game server region. Defaults to `ru`.

        Returns:
            Auction endpoint instance.
        """

        region = region or self._region

        return AuctionEndpoint(item_id=item_id, region=region, http=self._http, json=self._json)
