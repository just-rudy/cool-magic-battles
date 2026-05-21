from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities import CardType


class CardTypeRepository(ABC):
    @abstractmethod
    def save(self, card_type: CardType) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, card_type_id: UUID) -> CardType:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[CardType]:
        raise NotImplementedError

    @abstractmethod
    def find_by_title(self, title: str) -> CardType | None:
        raise NotImplementedError
