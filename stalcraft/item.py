from typing import Literal
import requests
import json

from . import LastCommitNotFound, ListingJsonNotFound, ItemIdNotFound


class Item:
    def __init__(self, name: str):
        self.name = name.lower()
        self.item_id = ""
        self.items_database = {}

    def _check_item_id(self):
        if not self.item_id:
            raise ItemIdNotFound(f"Item with name '{self.name}' not found")

    def __repr__(self):
        return f"<Item> name='{self.name}' item_id='{self.item_id}'"


class LocalItem(Item):
    def __init__(self, name: str, path: str="stalcraft/items.json", encoding="utf-8"):
        """
        Search for Item ID by name in file

        name: Name of item (without quotes)
        path: Path to the file, by default built-in stalcraft/items.json
        encoding: File encoding, default utf-8
        """

        super().__init__(name)

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
            if self.name in (lines['ru'], lines['en']):
                self.item_id = item_id
                break

    def __repr__(self):
        return f"<LocalItem> name='{self.name}' item_id='{self.item_id}' path='{self.path}' encoding='{self.encoding}'"


class WebItem(Item):
    def __init__(self, name: str, branch="main", region: Literal["ru"] | Literal ["global"] = "ru"):
        """
        Attention: This method is not most reliable and with frequent use may cause a rate limit
        Learn more: https://docs.github.com/en/rest/rate-limit

        Search for Item ID by name in stalcraft-database github repository

        name: Name of item (without quotes)
        branch: Default branch in repository
        region: Search folder ru/global, default ru
        """

        super().__init__(name)

        self.branch = branch
        self.region = region

        self.last_commit = ""

        self._get_last_commit()
        self._get_listing()
        self._find_item()

        self._check_item_id()

    def _get_last_commit(self):
        response = requests.get(f"https://api.github.com/repos/EXBO-Studio/stalcraft-database/branches/{self.branch}")
        branch_data = response.json()

        self.last_commit = branch_data.get("commit", {}).get("sha", "")

    def _get_listing(self):
        if not self.last_commit:
            raise LastCommitNotFound()

        listing = f"https://raw.githubusercontent.com/EXBO-Studio/stalcraft-database/{self.last_commit}/{self.region}/listing.json"

        response = requests.get(listing)

        self.items_database = response.json()

    def _format_line(self, value: str):
        return value.replace('«', '').replace('»', '').lower()

    def _find_item(self):
        if not self.items_database:
            raise ListingJsonNotFound()

        for item in self.items_database:
            lines = item.get("name", {}).get("lines", {})

            ru = lines.get("ru")
            en = lines.get("en")

            if self.name in (self._format_line(ru), self._format_line(en)):
                data = item.get("data", '').split('/')
                item_id = data[-1].split('.')[0]

                self.item_id = item_id

    def __repr__(self):
        return f"<WebItem> name='{self.name}' item_id='{self.item_id}'"
