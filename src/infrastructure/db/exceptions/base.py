class RepositoryError(Exception):
    """
    Base class for all infrastructure/database-related errors.
    All custom exceptions should inherit from this class.
    """
