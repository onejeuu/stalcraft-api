from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetadataKey(StrEnum):
    LAST_COMMIT = auto()
    LAST_UPDATED = auto()
    LAST_CHEKED = auto()
