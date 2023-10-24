from typing import Any, List, TypeVar


T = TypeVar("T")


class BaseListing(List[T]):
    def __init__(self, items: List[T], total: int = 0):
        super().__init__(items)
        self.total = total


class Listing(BaseListing[T]):
    """
    Usual python list with additional property "total".

    Which is needed to specify total number of game items in database.
    """

    DATA_NAME = "data"
    TOTAL_NAME = "total"

    def __init__(
        self,
        response: Any,
        schema: Any,
        data_name: str = DATA_NAME,
        total_name: str = TOTAL_NAME
    ):
        items = [
            schema.parse_obj(entry)
            for entry in response[data_name]
        ]
        total = response.get(total_name, 0)
        super().__init__(items, total)
