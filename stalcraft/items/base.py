from stalcraft.exceptions import ItemIdNotFound


class BaseItem:
    def __init__(self, name: str):
        self.name = name.lower()
        self.item_id = ""
        self.items = {}

    def _validate_item_id(self) -> None:
        if not self.item_id:
            raise ItemIdNotFound(f"Item with name '{self.name}' not found")

    def parse(self) -> str:
        return self.item_id

    def __str__(self):
        return self.item_id

    def __repr__(self):
        return f"<{self.__class__.__name__}> name='{self.name}' item_id='{self.item_id}'"
