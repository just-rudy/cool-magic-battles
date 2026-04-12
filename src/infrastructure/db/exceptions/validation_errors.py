from infrastructure.db.exceptions.base import RepositoryError


class EntityValidationError(RepositoryError):
    """
    Raised when entity data is invalid before persistence.
    Example:
    - empty username
    - negative values
    - missing required fields
    """
