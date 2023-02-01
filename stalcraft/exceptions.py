class InvalidToken(Exception):
    pass


class StalcraftApiException(Exception):
    pass


class Unauthorised(StalcraftApiException):
    pass


class InvalidParameter(StalcraftApiException):
    pass


class NotFound(StalcraftApiException):
    pass


class RateLimit(StalcraftApiException):
    pass


class ItemException(Exception):
    pass


class ListingJsonNotFound(ItemException):
    pass


class ItemIdNotFound(ItemException):
    pass
