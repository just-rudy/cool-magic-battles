from typing import Callable

import pytest

from application.services.deck_service import DeckService
from domain.entities.card import Card
from domain.entities.deck import Deck


def test_draw_returns_requested_number_of_cards(
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    c1 = make_card(title="c1")
    c2 = make_card(title="c2")
    c3 = make_card(title="c3")
    deck = make_deck(cards=[c1, c2, c3])

    drawn = service.draw(deck, 2)

    assert drawn == [c1, c2]
    assert deck.cards == [c3]


def test_draw_returns_all_cards_when_requested_all(
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    c1 = make_card(title="c1")
    c2 = make_card(title="c2")
    c3 = make_card(title="c3")
    deck = make_deck(cards=[c1, c2, c3])

    drawn = service.draw(deck, 3)

    assert drawn == [c1, c2, c3]
    assert deck.cards == []


def test_draw_raises_error_when_num_is_zero(
    make_deck: Callable[..., Deck],
) -> None:
    service = DeckService()
    deck = make_deck(cards=[])

    with pytest.raises(ValueError, match="Number of cards to draw must be positive."):
        service.draw(deck, 0)


def test_draw_raises_error_when_num_is_negative(
    make_deck: Callable[..., Deck],
) -> None:
    service = DeckService()
    deck = make_deck(cards=[])

    with pytest.raises(ValueError, match="Number of cards to draw must be positive."):
        service.draw(deck, -1)


def test_draw_raises_error_deck_empty(
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    deck = make_deck(cards=[make_card()])

    with pytest.raises(ValueError, match="Not enough cards in the deck to draw."):
        service.draw(deck, 2)


def test_draw_raises_error_when_not_enough_cards(
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    c1 = make_card(title="c1")
    c2 = make_card(title="c2")
    c3 = make_card(title="c3")
    deck = make_deck(cards=[c1, c2, c3])

    with pytest.raises(ValueError, match="Not enough cards in the deck to draw."):
        service.draw(deck, 4)


def test_shuffle_changes_card_order(
    monkeypatch: pytest.MonkeyPatch,
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    c1 = make_card(title="c1")
    c2 = make_card(title="c2")
    c3 = make_card(title="c3")
    deck = make_deck(cards=[c1, c2, c3])

    def fake_shuffle(cards: list[Card]) -> None:
        cards.reverse()

    monkeypatch.setattr(
        "application.services.deck_service.random.shuffle", fake_shuffle
    )

    service.shuffle(deck)

    assert deck.cards == [c3, c2, c1]


def test_is_empty_returns_true_for_empty_deck(
    make_deck: Callable[..., Deck],
) -> None:
    service = DeckService()
    deck = make_deck(cards=[])

    assert service.is_empty(deck) is True


def test_is_empty_returns_false_for_non_empty_deck(
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    service = DeckService()
    deck = make_deck(cards=[make_card()])

    assert service.is_empty(deck) is False
