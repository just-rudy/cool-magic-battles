from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities import Game


class GameRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, game_id: UUID) -> Game:
        raise NotImplementedError

    @abstractmethod
    def delete(self, game_id: UUID) -> None:
        raise NotImplementedError

    @abstractmethod
    def exists(self, game_id: UUID) -> bool:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Game]:
        raise NotImplementedError

    @abstractmethod
    def get_by_name(self, name: str) -> Game | None:
        raise NotImplementedError
