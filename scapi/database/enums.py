from enum import auto

from strenum import LowercaseStrEnum as StrEnum


class MetaKey(StrEnum):
    VERSION = "_version"
    SCHEMA = "_schema"
    CURRENT_COMMIT = auto()
    NORMALIZE_STATUS = auto()
    LAST_SYNC_STATUS = auto()
    LAST_SYNC_MODE = auto()
    LAST_TIME_CHECK = auto()
    LAST_TIME_SYNC = auto()
    LAST_TIME_NORMALIZE = auto()


class SyncMode(StrEnum):
    INDEX = DEFAULT = auto()
    ARCHIVE = FULL = auto()


class StatusSync(StrEnum):
    SYNCED = auto()
    UNCHANGED = auto()


class StatusNormalize(StrEnum):
    READY = auto()
    OUTDATED = auto()
