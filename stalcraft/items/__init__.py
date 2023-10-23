from typing import TypeAlias

from .local import LocalItem
from .web import WebItem


ItemId: TypeAlias = str | LocalItem | WebItem
