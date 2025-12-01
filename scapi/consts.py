class BaseUrl:
    """Base URLs for API endpoints."""

    DEMO = "http://dapi.stalcraft.net"
    EXTERNAL = PRODUCTION = "http://eapi.stalcraft.net"
    OAUTH = "https://exbo.net/oauth"


class DatabaseRepository:
    """Git Repository storing game entity ids, data and translations."""

    OWNER = "EXBO-Studio"
    REPOSITORY = "stalcraft-database"
    BRANCH = "main"


class Defaults:
    """Default constant values."""

    # Client
    BASE_URL: str = BaseUrl.PRODUCTION
    TIMEOUT: int = 60
    JSON: bool = False

    # OAuth
    REDIRECT_URI: str = "http://localhost"
    SCOPE: str = ""
