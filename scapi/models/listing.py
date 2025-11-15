from typing import Any, List, TypeVar

from pydantic import BaseModel


M = TypeVar("M", bound=BaseModel)


class BaseListing(List[M]):
    def __init__(self, items: List[M], total: int = 0):
        super().__init__(items)
        self.total = total


class Listing(BaseListing[M]):
    DATA_NAME = "data"
    TOTAL_NAME = "total"

    def __init__(
        self,
        response: Any,
        model: type[M],
        data_name: str = DATA_NAME,
        total_name: str = TOTAL_NAME,
    ):
        items = [model.model_validate(entry) for entry in response[data_name]]
        total = response.get(total_name, len(items))
        super().__init__(items, total)
