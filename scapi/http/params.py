from typing import Any, Dict, TypeAlias
from urllib.parse import urlencode


QueryParams: TypeAlias = Dict[str, Any]


class Params:
    def __init__(self, **kwargs: Any) -> None:
        self._data = {k: str(v) for k, v in kwargs.items() if v is not None}

    def to_dict(self) -> Dict[str, Any]:
        return self._data.copy()

    def __str__(self) -> str:
        return urlencode(self._data)
