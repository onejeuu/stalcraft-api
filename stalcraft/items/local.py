import json
from pathlib import Path

from stalcraft.defaults import Default
from stalcraft.enums import ItemsFolder
from stalcraft.items.base import BaseItem


class LocalItem(BaseItem):
    def __init__(self, name: str, folder: ItemsFolder = Default.ITEMS_FOLDER):
        """
        Search for Item ID by name in built-in file.

        Args:
            name: Name of item (without quotes).
            folder: Search folder ("ru" or "global").

        Raises:
            ItemIdNotFound: if item with this name not found.
        """

        super().__init__(name)

        root = Path(__file__).resolve().parent

        self.path = Path(root / "listing" / folder / "listing.json")

        self._load_items_from_file()
        self._find_item_id()

        self._validate_item_id()

    def _load_items_from_file(self) -> None:
        with open(self.path, "r", encoding="utf-8") as f:
            self.items = json.load(f)

    def _find_item_id(self) -> None:
        for item_id, lines in self.items.items():
            if self.name in (lines["ru"], lines["en"]):
                self.item_id = item_id
                break

    def __repr__(self):
        return f"{super().__repr__()} path='{self.path}'"
