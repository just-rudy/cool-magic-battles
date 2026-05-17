from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, user_id: UUID) -> User:
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, user_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def get_by_username(self, username: str) -> User | None:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[User]:
        raise NotImplementedError
