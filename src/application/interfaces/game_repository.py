from abc import ABC, abstractmethod
from uuid import UUID
from domain.entities.game import Game


class GameRepository(ABC):
    @abstractmethod
    def save(self, game: Game) -> None:
        pass

    @abstractmethod
    def get(self, game_id: UUID) -> Game:
        pass
