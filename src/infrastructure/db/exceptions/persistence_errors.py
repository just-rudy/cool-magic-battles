from infrastructure.db.exceptions.base import RepositoryError


class PersistenceError(RepositoryError):
    """
    Raised when database operation fails.
    Usually wraps SQLAlchemy errors like:
    - IntegrityError
    - SQLAlchemyError
    """
