from enum import Enum
from typing import Any, Dict

from stalcraft.exceptions import StalcraftApiException


class Params:
    MAX_LIMIT = 200

    def __init__(self, **kwargs: Any):
        self.params = {
            key: value.value if isinstance(value, Enum) else value
            for key, value in kwargs.items()
        }
        self._validate_limit_and_offset()

    @property
    def _max_limit(self):
        return self.MAX_LIMIT

    def _validate_limit_and_offset(self) -> None:
        if "limit" in self.params:
            self._validate_limit()

        if "offset" in self.params:
            self._validate_offset()

    def _validate_limit(self):
        limit = self.params.get("limit", 0)
        if limit not in range(self._max_limit + 1):
            raise StalcraftApiException(
                f"limit parameter should be between 0 and {self._max_limit}, got {limit}"
            )

    def _validate_offset(self):
        offset = self.params.get("offset", 0)
        if offset < 0:
            raise StalcraftApiException(
                f"offset parameter should be >= 0, got {offset}"
            )

    def parse(self) -> Dict[str, Any]:
        return self.params

    def __str__(self):
        return "&".join([f"{key}={value}" for key, value in self.params.items()])
