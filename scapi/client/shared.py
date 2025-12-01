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
    """Base API client for shared endpoints."""

    def __init__(
        self,
        *,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON,
    ):
        """
        Initialize shared client.

        Args:
            base_url (optional): API server base URL. Defaults to PRODUCTION.
            json (optional): Return raw JSON instead of validated models. Defaults to False.
        """

        self._base_url = base_url
        self._json = json
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
        region: str | Region = Default.REGION,
    ) -> models.EmissionState:
        """
        Get current emission state.

        Args:
            region (optional): Game server region. Defaults to RU.

        Returns:
            Emission state.
        """

        response = await self._http.GET(
            url=f"{region}/emission",
        )

        return self._parse(response, models.EmissionState)

    async def profile(
        self,
        username: str,
        region: str | Region = Default.REGION,
    ) -> models.CharacterProfile:
        """
        Retrieve public character profile including alliance, stats, and clan affiliation.

        Args:
            username: Character name.
            region (optional): Game server region. Defaults to RU.

        Returns:
            Public character profile data.
        """

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
        """
        List all registered clans.

        Args:
            limit (optional): Amount of clans to return, starting from offset, (0-100). Defaults to 20.
            offset (optional): Amount of clans to skip. Defaults to 0.
            region (optional): Game server region. Defaults to RU.

        Returns:
            Paginated clan listing.
        """

        response = await self._http.GET(
            url=f"{region}/clans",
            params=Params(limit=limit, offset=offset),
        )

        return self._parse(response, models.ClanInfo, ("data", "totalClans"))

    async def operations_sessions(
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
        """
        Returns list of operation sessions.

        Args:
            limit (optional): Amount of sessions to return, starting from offset, (0-100). Defaults to 20.
            offset (optional): Amount of sessions to skip. Defaults to 0.
            sort (optional): Sorting field. Defaults to DATE_FINISH.
            order (optional): Sorting direction. Defaults to ASCENDING.
            map (optional): Filter by operations map name.
            username (optional): Filter by character name.
            before (optional): Filter sessions ending before date.
            after (optional): Filter sessions ending after date.
            region (optional): Game server region. Defaults to RU.

        Returns:
            Paginated operations sessions listing.
        """

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
        """
        Factory method for auction endpoint operations.

        Args:
            item_id: Item identifier.
            region (optional): Game server region. Defaults to RU.

        Returns:
            Auction endpoint instance.
        """

        return AuctionEndpoint(item_id=item_id, region=region, http=self._http, json=self._json)
