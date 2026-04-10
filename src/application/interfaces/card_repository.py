from abc import ABC, abstractmethod
from uuid import UUID
from domain.entities.card import Card


class CardRepository(ABC):
    @abstractmethod
    def save(self, card: Card) -> None:
        raise NotImplementedError

    @abstractmethod
    def get(self, card_id: UUID) -> Card:
        raise NotImplementedError

    @abstractmethod
    def list_all(self) -> list[Card]:
        raise NotImplementedError
