from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetadataKey(StrEnum):
    MODE = auto()
    COMMIT = auto()
    UPDATED = auto()
    CHEKED = auto()
    STATUS = auto()
