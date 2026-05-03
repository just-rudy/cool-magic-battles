from application.services import CardLogic
from typing import Callable

from domain.entities import Card, Player


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


def test_apply_effect_adds_card_echo_to_current_echo(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(cur_echo=2)
    card = make_card(echo=3)

    logic.apply_effect(player, card)

    assert player.cur_echo == 5
