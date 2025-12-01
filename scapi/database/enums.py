from strenum import LowercaseStrEnum as StrEnum


class IndexFile(StrEnum):
    """Index files supporting entity search."""

    LISTING = "listing.json"
    ACHIEVEMENTS = "achievements.json"
    STATS = "stats.json"
