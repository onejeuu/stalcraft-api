class ItemIdException(Exception):
    pass


class LastCommitNotFound(ItemIdException):
    pass


class ListingJsonNotFound(ItemIdException):
    pass


class ItemIdNotFound(ItemIdException):
    pass
