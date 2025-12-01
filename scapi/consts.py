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
