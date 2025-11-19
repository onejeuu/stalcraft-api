from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetadataKey(StrEnum):
    MODE = auto()
    COMMIT = auto()
    UPDATED = auto()
    CHEKED = auto()
    STATUS = auto()


class SyncMode(StrEnum):
    INDEX = DEFAULT = auto()
    ARCHIVE = FULL = auto()


class ParseMode(StrEnum):
    INDEX = DEFAULT = auto()
    ITEMS = auto()
    FULL = auto()
