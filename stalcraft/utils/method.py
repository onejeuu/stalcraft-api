from enum import Enum
from pathlib import Path
from typing import Any


class Method:
    def __init__(self, *args: Any):
        self.path = Path()

        for arg in args:
            if isinstance(arg, Enum):
                arg = arg.value
            self.path /= str(arg)

    def parse(self) -> str:
        return self.path.as_posix()

    def __str__(self):
        return self.path.as_posix()
