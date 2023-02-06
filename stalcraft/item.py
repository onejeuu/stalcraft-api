from typing import Literal
import requests
import json
import os

from .enums import StatusCode

from .exceptions import (
    ListingJsonNotFound, ItemIdNotFound
)


class Item:
    def __init__(self, name: str):
        self.name = name.lower()
        self.item_id = ""
        self.items_database = {}

    def _check_item_id(self):
        if not self.item_id:
            raise ItemIdNotFound(f"Item with name '{self.name}' not found")

    def __str__(self):
        return self.item_id

    def __repr__(self):
        return f"<{self.__class__.__name__}> name='{self.name}' item_id='{self.item_id}'"



class LocalItem(Item):
    def __init__(self, name: str, path="", encoding="utf-8"):
        """
        Search for Item ID by name in file

        name: Name of item (without quotes)
        path: Path to the file, by default built-in items.json
        encoding: File encoding, default utf-8
        """

        super().__init__(name)

        if not path:
            here = os.path.abspath(os.path.dirname(__file__))
            path = f"{here}/data/items.json"

        self.path = path
        self.encoding = encoding

        self._load_from_file()
        self._find_item()

        self._check_item_id()

    def _load_from_file(self):
        with open(self.path, "r", encoding=self.encoding) as f:
            self.items_database = json.load(f)

    def _find_item(self):
        for item_id, lines in self.items_database.items():
            if self.name in (lines["ru"], lines["en"]):
                self.item_id = item_id
                break

    def __repr__(self):
        return f"{super().__repr__()} path='{self.path}' encoding='{self.encoding}'"


class WebItem(Item):
    GITHUB_RAW = "raw.githubusercontent.com"
    REPOS = "EXBO-Studio/stalcraft-database"
    DEFAULT_BRANCH = "main"

    def __init__(self, name: str, folder: Literal["ru", "global"] = "ru"):
        """
        Attention: This method is not most reliable and with frequent use may cause a rate limit
        Learn more: https://docs.github.com/en/rest/rate-limit

        Search for Item ID by name in stalcraft-database github repository

        name: Name of item (without quotes)
        folder: Search folder ru/global, default ru
        """

        super().__init__(name)

        self.folder = folder

        self._get_listing()
        self._find_item()

        self._check_item_id()

    def _get_listing(self):
        response = requests.get(
            f"http://{self.GITHUB_RAW}/{self.REPOS}/{self.DEFAULT_BRANCH}/{self.folder}/listing.json"
        )

        if response.status_code != StatusCode.OK.value:
            raise ListingJsonNotFound(f"Listing.json not found in '{self.REPOS}/{self.DEFAULT_BRANCH}/{self.folder}'")

        self.items_database = response.json()

    def _format(self, name: str):
        return name.replace('«', '').replace('»', '').lower()

    def _find_item(self):
        for item in self.items_database:
            lines = item.get("name", {}).get("lines", {})

            ru = self._format(lines.get("ru", ''))
            en = self._format(lines.get("en", ''))

            if self.name in (ru, en):
                data = item.get("data", '')
                file_name, file_extension = data.split('/')[-1].split('.')
                item_id = file_name

                self.item_id = item_id
                break

    def __repr__(self):
        return f"{super().__repr__()} folder='{self.folder}'"
