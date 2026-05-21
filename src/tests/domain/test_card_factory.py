from application.services.card_factory import generate_cards, list_card_types
from domain.enums import CardAction, UsePattern


def test_list_card_types_respects_generation_rules() -> None:
    card_types = list_card_types()

    assert card_types
    for card_type in card_types:
        if card_type.if_permanent:
            assert card_type.action in {
                CardAction.HAND_BUFF,
                CardAction.ECHO_BUFF,
            }

        if card_type.action == CardAction.DEF:
            assert card_type.usage_pattern in {
                UsePattern.DISCARD,
                UsePattern.ON_TOP,
            }

        if card_type.action in {CardAction.ATTACK, CardAction.DRAW}:
            assert card_type.usage_pattern == UsePattern.REG

        if card_type.action == CardAction.HEAL:
            assert card_type.usage_pattern != UsePattern.ON_TOP


def test_generate_cards_assigns_known_card_type_ids() -> None:
    known_type_ids = {card_type.id for card_type in list_card_types()}

    cards = generate_cards(25)

    assert len(cards) == 25
    assert all(card.card_type_id in known_type_ids for card in cards)
    assert all(card.image is not None for card in cards)
    assert all(
        card.image_id == card.image.id for card in cards if card.image is not None
    )
