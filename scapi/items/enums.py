from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetadataKey(StrEnum):
    COMMIT = auto()
    UPDATED = auto()
    CHEKED = auto()
    STATUS = auto()
