import json


class Item:
    def __init__(self, name: str):
        self.items = json.loads(open("stalcraft/items.json", "r", encoding="utf-8").read())

        self.name = name.lower()
        self.item_id = ""

        for item_id, lines in self.items.items():

            ru = lines['ru']
            en = lines['en']

            if ru == self.name or en == self.name:
                self.item_id = item_id

        if not self.item_id:
            raise ValueError(f"Item {self.name} not found")

    def __repr__(self):
        return f"<Item> name='{self.name}' item_id='{self.item_id}'"
