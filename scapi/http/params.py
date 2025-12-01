from typing import Any, Dict, TypeAlias
from urllib.parse import urlencode


QueryParams: TypeAlias = Dict[str, str]


class Params:
    """HTTP query parameter container."""

    def __init__(self, **kwargs: Any) -> None:
        self._data: QueryParams = {k: str(v) for k, v in kwargs.items() if v is not None}

    def to_dict(self) -> QueryParams:
        return self._data.copy()

    def __str__(self) -> str:
        return urlencode(self._data)
