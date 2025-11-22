from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetaKey(StrEnum):
    _VERSION = auto()
    _SCHEMA = auto()
    CURRENT_COMMIT = auto()
    LAST_SYNC_MODE = auto()
    LAST_SYNC_STATUS = auto()
    LAST_TIME_CHECK = auto()
    LAST_TIME_SYNC = auto()
    LAST_TIME_NORMALIZE = auto()


class MetaStatus(StrEnum):
    SYNCED = auto()
    NORMALIZED = auto()
    UNCHANGED = auto()


class SyncMode(StrEnum):
    INDEX = DEFAULT = auto()
    ARCHIVE = FULL = auto()
