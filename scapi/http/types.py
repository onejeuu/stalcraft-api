from typing import Any, List, TypeVar

from pydantic import BaseModel


M = TypeVar("M", bound=BaseModel)


class BaseListing(List[M]):
    def __init__(self, items: List[M], total: int = 0):
        super().__init__(items)
        self.total = total


class Listing(BaseListing[M]):
    _KEY_DATA = "data"
    _KEY_TOTAL = "total"

    def __init__(
        self,
        response: Any,
        model: type[M],
        key_data: str = _KEY_DATA,
        key_total: str = _KEY_TOTAL,
    ):
        items = [model.model_validate(entry) for entry in response[key_data]]
        total = response.get(key_total, len(items))
        super().__init__(items, total)
