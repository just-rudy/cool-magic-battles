from abc import ABC, abstractmethod
from uuid import UUID
from domain.entities.user import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> None:
        pass

    @abstractmethod
    def get(self, user_id: UUID) -> User:
        pass
