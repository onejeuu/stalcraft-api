from typing import Any, List, TypeVar


T = TypeVar("T")


class BaseListing(List[T]):
    def __init__(self, items: List[T], total: int=0):
        super().__init__(items)
        self.total = total


class Listing(BaseListing[T]):
    """
    Usual python list with additional property "total".

    Which is needed to specify total number of game items in database.
    """

    def __init__(
        self,
        response: Any,
        schema: Any,
        data_name: str = "data",
        total_name: str = "total"
    ):
        items = [
            schema.parse_obj(entry)
            for entry in response[data_name]
        ]
        total = response.get(total_name, 0)
        super().__init__(items, total)
