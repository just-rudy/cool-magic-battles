from collections import Counter

from application.services.card_factory import (
    ACTION_WEIGHTS,
    CARD_STATS,
    generate_cards,
    list_card_types,
)
from domain.card_colors import ACTION_COLORS
from domain.enums import CardAction, UsePattern


def test_list_card_types_respects_generation_rules() -> None:
    card_types = list_card_types()

    assert card_types
    for card_type in card_types:
        # DEF только через discard или on_top
        if card_type.action == CardAction.DEF:
            assert card_type.usage_pattern in {
                UsePattern.DISCARD,
                UsePattern.ON_TOP,
            }, f"DEF card has wrong usage_pattern: {card_type.usage_pattern}"

        # ATTACK и DRAW — только reg
        if card_type.action in {CardAction.ATTACK, CardAction.DRAW}:
            msg = (
                f"{card_type.action} card has wrong "
                f"usage_pattern: {card_type.usage_pattern}"
            )
            assert card_type.usage_pattern == UsePattern.REG, msg

        # HAND_BUFF и ECHO_BUFF — только banish
        if card_type.action in {CardAction.HAND_BUFF, CardAction.ECHO_BUFF}:
            msg = (
                f"{card_type.action} card has wrong "
                f"usage_pattern: {card_type.usage_pattern}"
            )
            assert card_type.usage_pattern == UsePattern.BANISH, msg

        # HEAL — не on_top
        if card_type.action == CardAction.HEAL:
            assert card_type.usage_pattern != UsePattern.ON_TOP, (
                f"HEAL card has wrong usage_pattern: {card_type.usage_pattern}"
            )

        assert card_type.color == ACTION_COLORS[card_type.action]


def test_generate_cards_assigns_known_card_type_ids() -> None:
    known_type_ids = {card_type.id for card_type in list_card_types()}

    cards = generate_cards(25)

    assert len(cards) == 25
    assert all(card.card_type_id in known_type_ids for card in cards)
    assert all(card.image is not None for card in cards)
    assert all(
        card.image_id == card.image.id for card in cards if card.image is not None
    )


def test_card_stats_power_limits() -> None:
    """Проверяет что диапазоны силы соответствуют балансу."""
    # HAND_BUFF и ECHO_BUFF — сила только 1
    assert CARD_STATS[CardAction.HAND_BUFF].power_range == (1, 1)
    assert CARD_STATS[CardAction.ECHO_BUFF].power_range == (1, 1)

    # DRAW — не больше 3
    assert CARD_STATS[CardAction.DRAW].power_range[1] <= 3

    # HEAL — не больше 3
    assert CARD_STATS[CardAction.HEAL].power_range[1] <= 3

    # ATTACK — от 1 до 5
    assert CARD_STATS[CardAction.ATTACK].power_range == (1, 5)


def test_action_weights_balance() -> None:
    """Проверяет что веса соответствуют балансу."""
    # ATTACK встречается чаще всего
    assert ACTION_WEIGHTS[CardAction.ATTACK] > ACTION_WEIGHTS[CardAction.DEF]
    assert ACTION_WEIGHTS[CardAction.ATTACK] > ACTION_WEIGHTS[CardAction.DRAW]
    assert ACTION_WEIGHTS[CardAction.ATTACK] > ACTION_WEIGHTS[CardAction.HEAL]

    # DEF встречается реже ATTACK
    assert ACTION_WEIGHTS[CardAction.DEF] < ACTION_WEIGHTS[CardAction.ATTACK]

    # HAND_BUFF и ECHO_BUFF встречаются редко
    assert ACTION_WEIGHTS[CardAction.HAND_BUFF] < ACTION_WEIGHTS[CardAction.ATTACK]
    assert ACTION_WEIGHTS[CardAction.ECHO_BUFF] < ACTION_WEIGHTS[CardAction.ATTACK]
    assert ACTION_WEIGHTS[CardAction.HAND_BUFF] < ACTION_WEIGHTS[CardAction.DEF]
    assert ACTION_WEIGHTS[CardAction.ECHO_BUFF] < ACTION_WEIGHTS[CardAction.DEF]


def test_generated_cards_respect_power_limits() -> None:
    """Генерирует 200 карт и проверяет что все статы в допустимых диапазонах."""
    cards = generate_cards(200)
    known_type_ids = {ct.id: ct for ct in list_card_types()}

    for card in cards:
        ct = known_type_ids[card.card_type_id]
        stats = CARD_STATS[ct.action]

        assert stats.power_range[0] <= card.power <= stats.power_range[1], (
            f"{ct.action} card '{card.title}' has power={card.power}, "
            f"expected {stats.power_range}"
        )
        assert stats.echo_range[0] <= card.echo <= stats.echo_range[1], (
            f"{ct.action} card '{card.title}' has echo={card.echo}, "
            f"expected {stats.echo_range}"
        )
        assert stats.cost_range[0] <= card.cost <= stats.cost_range[1], (
            f"{ct.action} card '{card.title}' has cost={card.cost}, "
            f"expected {stats.cost_range}"
        )


def test_generated_cards_attack_frequency() -> None:
    """Проверяет что ATTACK карты встречаются чаще всего в большой выборке."""
    cards = generate_cards(500)
    known_type_ids = {ct.id: ct for ct in list_card_types()}

    action_counts: Counter[CardAction] = Counter()
    for card in cards:
        ct = known_type_ids[card.card_type_id]
        action_counts[ct.action] += 1

    # ATTACK должен быть самым частым
    most_common_action = action_counts.most_common(1)[0][0]
    assert most_common_action == CardAction.ATTACK, (
        f"Expected ATTACK to be most common, got {most_common_action}. "
        f"Counts: {dict(action_counts)}"
    )

    # HAND_BUFF и ECHO_BUFF должны быть редкими (меньше 15% каждый)
    total = len(cards)
    for rare_action in (CardAction.HAND_BUFF, CardAction.ECHO_BUFF):
        ratio = action_counts[rare_action] / total
        assert ratio < 0.15, (
            f"{rare_action} appears too often: {ratio:.1%} (expected < 15%)"
        )
