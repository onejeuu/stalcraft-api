from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any, Optional

from httpx import QueryParams

from stalcraft import Region, schemas
from stalcraft.api.base import BaseApi
from stalcraft.auction import Auction
from stalcraft.defaults import Default
from stalcraft.enums import OperationSort, Order
from stalcraft.items import ItemId
from stalcraft.utils import Listing


class BaseClient(ABC):
    def __init__(
        self,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        self._base_url = base_url
        self.json = json

        self._api = self._get_api()

    @abstractmethod
    def _get_api(self) -> BaseApi:
        ...

    @property
    def ratelimit(self) -> schemas.RateLimit:
        return self._api.ratelimit

    def regions(self) -> Any | list[schemas.RegionInfo]:
        """
        Returns list of regions which can be access by api calls.

        ! This method does not update RateLimit values.
        """

        response = self._api.request_get(
            Path("regions")
        )

        return response if self.json else [schemas.RegionInfo.model_validate(region) for region in response]

    def auction(
        self,
        item_id: ItemId,
        region: Region = Default.REGION
    ) -> Auction:
        """
        Factory method for working with auction.

        Args:
            item_id: Item ID. For example "1r756".
            region: Stalcraft server region.
        """

        return Auction(self._api, item_id, region, self.json)

    def emission(
        self,
        region: Region = Default.REGION
    ) -> Any | schemas.Emission:
        """
        Returns information about current emission, if any, and recorded time of the previous one.

        Args:
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Path(region, "emission")
        )

        return response if self.json else schemas.Emission.model_validate(response)

    def character_profile(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | schemas.CharacterProfile:
        """
        Returns information about players profile.
        Includes alliance, profile description, last login time, stats, etc.

        Args:
            character: Character name.
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Path(region, "character", "by-name", character, "profile")
        )

        return response if self.json else schemas.CharacterProfile.model_validate(response)

    def clans(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        region: Region = Default.REGION
    ) -> Any | Listing[schemas.ClanInfo]:
        """
        Returns all clans which are currently registered in the game on specified region.

        Args:
            limit: Amount of clans to return, starting from offset, (0-100). Defaults to 20.
            offset: Amount of clans in list to skip. Defaults to 0.
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Path(region, "clans"),
            QueryParams(limit=limit, offset=offset)
        )

        return response if self.json else Listing(response, schemas.ClanInfo, "data", "totalClans")

    def operations(
        self,
        limit: int = Default.LIMIT,
        offset: int = Default.OFFSET,
        sort: OperationSort = Default.OPERTATION_SORT,
        order: Order = Default.ORDER,
        map: Optional[str] = None,
        username: Optional[str] = None,
        before: Optional[datetime] = None,
        after: Optional[datetime] = None,
        region: Region = Default.REGION,
    ) -> Any | Listing[schemas.ClanInfo]:
        """
        Returns list of operation sessions on specified region.

        Args:
            limit: Amount of sessions to return, starting from offset, (0-100). Defaults to 20.
            offset: Amount of sessions in list to skip. Defaults to 0.
            sort: Property to sort by. Defaults to DATE_FINISH.
            order: Either asc or desc. Defaults to ASCENDING.
            map: Filter by operation map.
            username: Filter by player username.
            before: Filter by date before.
            after: Filter by date after.
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Path(region, "operations/sessions"),
            QueryParams(
                limit=limit, offset=offset, sort=sort, order=order, map=map, username=username,
                before=before.strftime("%Y-%m-%dT%H:%M:%SZ") if before else None, after=after.strftime("%Y-%m-%dT%H:%M:%SZ") if after else None
            )
        )

        return response if self.json else Listing(response, schemas.OperationSession, "sessions", "total")

    def __str__(self):
        return f"<{self.__class__.__name__}> {self._api.__str__()}"
