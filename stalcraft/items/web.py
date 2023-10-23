from pathlib import Path
from typing import Any

import httpx

from stalcraft.consts import ItemsDatabase, StatusCode
from stalcraft.default import Default
from stalcraft.exceptions import ListingJsonNotFound
from stalcraft.items.base import BaseItem


class WebItem(BaseItem):
    def __init__(self, name: str, folder: str = Default.ITEMS_FOLDER):
        """
        Attention: This method is sync only.
        Attention: This method is not most reliable and with frequent use may cause a rate limit.

        Learn more: https://docs.github.com/en/rest/rate-limit

        Search for Item ID by name in stalcraft-database github repository.

        Args:
            name: Name of item (without quotes).
            folder: Search folder ("ru" or "global").

        Raises:
            ItemIdNotFound: if item with this name not found.
            ListingJsonNotFound: if response status code != 200.
        """

        super().__init__(name)

        self.folder = folder

        self.items = self._get_listing_json()
        self._find_item_id()

        self._validate_item_id()

    @property
    def _url(self) -> str:
        return f"https://{ItemsDatabase.GITHUB_RAW}/{ItemsDatabase.REPOS}/{ItemsDatabase.BRANCH}/{self.folder}/listing.json"

    @property
    def _part_of_url(self)  -> str:
        return f"{ItemsDatabase.REPOS}/{ItemsDatabase.BRANCH}/{self.folder}"

    def _validate_response_status(self, response: httpx.Response) -> None:
        if response.status_code != StatusCode.OK:
            raise ListingJsonNotFound(f"Listing.json not found in '{self._part_of_url}'")

    def _get_listing_json(self) -> Any:
        with httpx.Client() as client:
            response = client.get(self._url)

        self._validate_response_status(response)

        return response.json()

    def _format(self, name: str) -> str:
        return name.replace("«", "").replace("»", "").lower()

    def _find_item_id(self) -> None:
        if not self.items:
            return

        for item in self.items:
            lines = item.get("name", {}).get("lines", {})

            ru = self._format(lines.get("ru", ""))
            en = self._format(lines.get("en", ""))

            if self.name in (ru, en):
                data = item.get("data", "")
                file_name = Path(data).stem
                self.item_id = file_name
                break

    def __repr__(self):
        return f"{super().__repr__()} folder='{self.folder}'"
