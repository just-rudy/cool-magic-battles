from typing import Any
from uuid import UUID

from application.interfaces.card_repository import CardRepository
from domain.entities import Card


class CardController:
    def __init__(self, card_repository: CardRepository) -> None:
        self._card_repo = card_repository

    def list_cards(self) -> list[dict[str, Any]]:
        card_list = self._card_repo.list_all()
        return [
            {
                "id": str(card.id),
                "title": card.title,
                "creature": card.creature,
                "power": card.power,
                "echo": card.echo,
                "cost": card.cost,
                "cool_points": card.cool_points,
            }
            for card in card_list
        ]

    def get_card_by_id(self, card_id: UUID) -> Card:
        return self._card_repo.get(card_id)

    def show_card(self, card_id: UUID) -> dict[str, Any]:
        card = self._card_repo.get(card_id)
        if card is None:
            raise ValueError("Card not found")
        return {
            "id": str(card.id),
            "title": card.title,
            "creature": card.creature,
            "power": card.power,
            "echo": card.echo,
            "cost": card.cost,
            "cool_points": card.cool_points,
        }

    def show_rules(self) -> str:
        return "temporary just showin' the link\nfor rules see: https://www.mosigra.ru/download/rules/jepichnie-shvatki-boevih-magov-krutagidon-2025-rules.pdf"

    def get_card_by_title(self, title: str) -> Card:
        card = self._card_repo.find_by_title(title)

        if card is None:
            raise ValueError("Карта не найдена")

        return card
