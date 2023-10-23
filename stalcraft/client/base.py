from abc import ABC, abstractmethod
from typing import Any

from stalcraft import Auction, Region, schemas
from stalcraft.api import SecretApi, TokenApi
from stalcraft.default import Default
from stalcraft.items import ItemId
from stalcraft.utils import Listing, Method, Params


class BaseClient(ABC):
    _TOKEN_API = TokenApi
    _SECRET_API = SecretApi

    def __init__(
        self,
        base_url: str = Default.BASE_URL,
        json: bool = Default.JSON
    ):
        self._base_url = base_url
        self.json = json

        self._api = self._get_api()

    @abstractmethod
    def _get_api(self) -> _TOKEN_API | _SECRET_API:
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
            Method("regions")
        )

        return response if self.json else [schemas.RegionInfo.parse_obj(region) for region in response]

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
            Method(region, "emission")
        )

        return response if self.json else schemas.Emission.parse_obj(response)

    def character_profile(
        self,
        character: str,
        region: Region = Default.REGION
    ) -> Any | schemas.CharacterProfile:
        """
        Returns information about player's profile.
        Includes alliance, profile description, last login time, stats, etc.

        Args:
            character: Character name.
            region: Stalcraft server region.
        """

        response = self._api.request_get(
            Method(region, "character", "by-name", character, "profile")
        )

        return response if self.json else schemas.CharacterProfile.parse_obj(response)

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
            Method(region, "clans"),
            Params(limit=limit, offset=offset)
        )

        return response if self.json else Listing(response, schemas.ClanInfo, "data", "totalClans")

    def __str__(self):
        return f"<{self.__class__.__name__}> {self._api.__str__()}"
