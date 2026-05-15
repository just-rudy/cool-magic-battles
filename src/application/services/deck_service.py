import random

from domain.entities.card import Card
from domain.entities.deck import Deck


class DeckService:
    def draw(self, deck: Deck, num: int) -> list[Card]:
        if num <= 0:
            raise ValueError("Number of cards to draw must be positive.")
        if num > len(deck.cards):
            raise ValueError("Not enough cards in the deck to draw.")
        drawn_cards = deck.cards[:num]
        deck.cards = deck.cards[num:]
        return drawn_cards

    def shuffle(self, deck: Deck) -> None:
        random.shuffle(deck.cards)

    def is_empty(self, deck: Deck) -> bool:
        return len(deck.cards) == 0
