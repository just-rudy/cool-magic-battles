"""MongoDB-specific exceptions that map to the same interface as DB exceptions."""


class MongoEntityNotFoundError(Exception):
    pass


class MongoPersistenceError(Exception):
    pass
