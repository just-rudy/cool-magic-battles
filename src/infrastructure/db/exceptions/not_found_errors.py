from infrastructure.db.exceptions.base import RepositoryError


class EntityNotFoundError(RepositoryError):
    """
    Raised when requested entity is not found in the database.
    Example:
    - user does not exist
    - game not found by id
    """
