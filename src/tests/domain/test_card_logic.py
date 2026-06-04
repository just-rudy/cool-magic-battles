from collections.abc import Callable
from uuid import uuid4

import pytest

from application.services import CardLogic
from application.services.deck_service import DeckService
from domain.entities import Card, Player
from domain.entities.card_type import CardType
from domain.enums import CardAction, UsePattern


def _make_card_type(action: CardAction) -> CardType:
    return CardType(id=uuid4(), action=action, usage_pattern=UsePattern.REG)


def test_can_purchase_returns_true(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(base_echo=3, cur_echo=3)
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

    result = logic.apply_effect(player, card)

    assert player.cur_echo == 5
    assert result == 0


def test_apply_effect_attack_reduces_target_health(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(cur_echo=0)
    target = make_player(health=20)
    card = make_card(power=5, echo=1)
    card_type = _make_card_type(CardAction.ATTACK)

    damage = logic.apply_effect(player, card, card_type=card_type, target=target)

    assert damage == 5
    assert target.health == 20  # Урон не применяется в apply_effect для ATTACK
    assert player.cur_echo == 1


def test_apply_effect_attack_raises_when_no_target(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card(power=3)
    card_type = _make_card_type(CardAction.ATTACK)

    with pytest.raises(ValueError, match="ATTACK card requires a target player"):
        logic.apply_effect(player, card, card_type=card_type, target=None)


def test_apply_effect_heal_increases_target_health(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    target = make_player(health=10)
    card = make_card(power=5, echo=0)
    card_type = _make_card_type(CardAction.HEAL)

    result = logic.apply_effect(player, card, card_type=card_type, target=target)

    assert target.health == 15
    assert result == 0


def test_apply_effect_heal_caps_at_25(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    target = make_player(health=23)
    card = make_card(power=5, echo=0)
    card_type = _make_card_type(CardAction.HEAL)

    result = logic.apply_effect(player, card, card_type=card_type, target=target)

    assert target.health == 25
    assert result == 0


def test_apply_effect_heal_at_max_health_still_grants_echo(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(cur_echo=0)
    target = make_player(health=25)
    card = make_card(power=3, echo=2)
    card_type = _make_card_type(CardAction.HEAL)

    logic.apply_effect(player, card, card_type=card_type, target=target)

    assert target.health == 25
    assert player.cur_echo == 2


def test_apply_effect_heal_raises_when_no_target(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card(power=3)
    card_type = _make_card_type(CardAction.HEAL)

    with pytest.raises(ValueError, match="HEAL card requires a target player"):
        logic.apply_effect(player, card, card_type=card_type, target=None)


def test_apply_effect_def_only_adds_echo(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(cur_echo=0, health=20)
    card = make_card(power=3, echo=2)
    card_type = _make_card_type(CardAction.DEF)

    result = logic.apply_effect(player, card, card_type=card_type)

    assert player.cur_echo == 2
    assert player.health == 20
    assert result == 0


def test_apply_effect_draw_draws_cards_from_draw_deck(
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., object],
) -> None:
    logic = CardLogic()
    draw_cards = [make_card(title=f"draw_{i}") for i in range(5)]
    player = make_player()
    player.draw_deck.cards = list(draw_cards)

    card = make_card(power=3, echo=0)
    card_type = _make_card_type(CardAction.DRAW)
    deck_service = DeckService()

    result = logic.apply_effect(
        player, card, card_type=card_type, deck_service=deck_service
    )

    assert len(player.hand_deck.cards) == 3
    assert player.hand_deck.cards == draw_cards[:3]
    assert len(player.draw_deck.cards) == 2
    assert result == 0


def test_apply_effect_draw_draws_available_when_not_enough(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    draw_cards = [make_card(title="only_one")]
    player = make_player()
    player.draw_deck.cards = list(draw_cards)

    card = make_card(power=5, echo=0)
    card_type = _make_card_type(CardAction.DRAW)
    deck_service = DeckService()

    result = logic.apply_effect(
        player, card, card_type=card_type, deck_service=deck_service
    )

    assert len(player.hand_deck.cards) == 1
    assert len(player.draw_deck.cards) == 0
    assert result == 0


def test_apply_effect_draw_empty_deck_draws_nothing(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    player.draw_deck.cards = []

    card = make_card(power=3, echo=0)
    card_type = _make_card_type(CardAction.DRAW)
    deck_service = DeckService()

    result = logic.apply_effect(
        player, card, card_type=card_type, deck_service=deck_service
    )

    assert player.hand_deck.cards == []
    assert result == 0


def test_apply_effect_hand_buff_increases_hand_size(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(hand_size=5)
    card = make_card(power=2, echo=0)
    card_type = _make_card_type(CardAction.HAND_BUFF)

    result = logic.apply_effect(player, card, card_type=card_type)

    assert player.hand_size == 7
    assert result == 0


def test_apply_effect_echo_buff_increases_base_echo(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player(base_echo=1)
    card = make_card(power=3, echo=0)
    card_type = _make_card_type(CardAction.ECHO_BUFF)

    result = logic.apply_effect(player, card, card_type=card_type)

    assert player.base_echo == 4
    assert result == 0


def test_can_defend_returns_true_for_def_card_in_hand(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card()
    player.hand_deck.cards.append(card)
    card_type = CardType(
        id=uuid4(), action=CardAction.DEF, usage_pattern=UsePattern.DISCARD
    )

    result = logic.can_defend(player, card, card_type)

    assert result is True


def test_can_defend_returns_false_for_non_def_card(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card()
    player.hand_deck.cards.append(card)
    card_type = CardType(
        id=uuid4(), action=CardAction.ATTACK, usage_pattern=UsePattern.REG
    )

    result = logic.can_defend(player, card, card_type)

    assert result is False


def test_can_defend_returns_false_when_card_not_in_hand(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    player = make_player()
    card = make_card()
    card_type = CardType(
        id=uuid4(), action=CardAction.DEF, usage_pattern=UsePattern.DISCARD
    )

    result = logic.can_defend(player, card, card_type)

    assert result is False


def test_apply_defense_reduces_damage_and_moves_card_to_discard(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    defender = make_player(cur_echo=0)
    card = make_card(power=3, echo=1)
    defender.hand_deck.cards.append(card)
    card_type = CardType(
        id=uuid4(), action=CardAction.DEF, usage_pattern=UsePattern.DISCARD
    )

    remaining = logic.apply_defense(defender, card, card_type, incoming_damage=5)

    assert remaining == 2  # 5 - 3
    assert defender.cur_echo == 1
    assert card not in defender.hand_deck.cards
    assert card in defender.discard_deck.cards


def test_apply_defense_reduces_damage_to_zero(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    defender = make_player(cur_echo=0)
    card = make_card(power=10, echo=2)
    defender.hand_deck.cards.append(card)
    card_type = CardType(
        id=uuid4(), action=CardAction.DEF, usage_pattern=UsePattern.DISCARD
    )

    remaining = logic.apply_defense(defender, card, card_type, incoming_damage=5)

    assert remaining == 0
    assert defender.cur_echo == 2


def test_apply_defense_moves_card_on_top_of_draw_deck(
    make_player: Callable[..., Player], make_card: Callable[..., Card]
) -> None:
    logic = CardLogic()
    defender = make_player()
    existing_card = make_card(title="existing")
    defender.draw_deck.cards.append(existing_card)
    
    def_card = make_card(title="defense", power=3, echo=1)
    defender.hand_deck.cards.append(def_card)
    
    card_type = CardType(
        id=uuid4(), action=CardAction.DEF, usage_pattern=UsePattern.ON_TOP
    )

    remaining = logic.apply_defense(defender, def_card, card_type, incoming_damage=5)

    assert remaining == 2
    assert def_card not in defender.hand_deck.cards
    assert def_card in defender.draw_deck.cards
    assert defender.draw_deck.cards[0] == def_card  # На верху колоды
    assert defender.draw_deck.cards[1] == existing_card
