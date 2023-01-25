class ItemException(Exception):
    pass


class LastCommitNotFound(ItemException):
    pass


class ListingJsonNotFound(ItemException):
    pass


class ItemIdNotFound(ItemException):
    pass
