from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetaKey(StrEnum):
    _VERSION = auto()
    _SCHEMA = auto()
    CURRENT_COMMIT = auto()
    LAST_SYNC_MODE = auto()
    LAST_CHECK = auto()
    LAST_UPDATE = auto()
    LAST_NORMALIZE = auto()
    LAST_STATUS = auto()


class MetaStatus(StrEnum):
    SYNCED = auto()
    NORMALIZED = auto()
    UNCHANGED = auto()


class SyncMode(StrEnum):
    INDEX = DEFAULT = auto()
    ARCHIVE = FULL = auto()
