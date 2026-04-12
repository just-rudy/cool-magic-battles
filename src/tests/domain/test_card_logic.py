from application.services.card_logic import CardLogic
from typing import Callable

from domain.entities.card import Card
from domain.entities.player import Player


def test_can_purchase_returns_true(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(base_echo=2, cur_echo=2)
    card = make_card(cost=3)

    result = logic.can_purchase(player, card)

    assert result is True


def test_can_purchase_returns_false(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(base_echo=1, cur_echo=1)
    card = make_card(cost=5)

    result = logic.can_purchase(player, card)

    assert result is False


def test_can_be_played_returns_true(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card()

    player.hand_deck.cards.append(card)

    result = logic.can_be_played(player, card)

    assert result is True


def test_can_be_played_returns_false(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card()
    other_card = make_card()

    player.hand_deck.cards.append(other_card)

    result = logic.can_be_played(player, card)

    assert result is False
