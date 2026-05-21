import random
import re
from functools import lru_cache
from uuid import NAMESPACE_URL, uuid4, uuid5

from domain.entities import Card, CardType, Image
from domain.enums import CardAction, UsePattern

CARD_TYPE_NAMESPACE = uuid5(NAMESPACE_URL, "cool-magic-battles/card-types")
CARD_IMAGE_NAMESPACE = uuid5(NAMESPACE_URL, "cool-magic-battles/card-images")
CARD_TYPE_COLORS = ("red", "blue", "green", "yellow", "pink", "orange")


def _build_card_type(
    action: CardAction,
    usage_pattern: UsePattern,
    *,
    if_permanent: bool,
    color: str,
) -> CardType:
    card_type_key = f"{action.value}:{usage_pattern.value}:{int(if_permanent)}:{color}"
    return CardType(
        id=uuid5(CARD_TYPE_NAMESPACE, card_type_key),
        action=action,
        usage_pattern=usage_pattern,
        if_permanent=if_permanent,
        color=color,
    )


@lru_cache(maxsize=1)
def list_card_types() -> tuple[CardType, ...]:
    card_types: list[CardType] = []

    for color in CARD_TYPE_COLORS:
        for action in (CardAction.ATTACK, CardAction.DRAW):
            card_types.append(
                _build_card_type(
                    action,
                    UsePattern.REG,
                    if_permanent=False,
                    color=color,
                )
            )

        for usage_pattern in (UsePattern.DISCARD, UsePattern.ON_TOP):
            card_types.append(
                _build_card_type(
                    CardAction.DEF,
                    usage_pattern,
                    if_permanent=False,
                    color=color,
                )
            )

        for usage_pattern in (UsePattern.REG, UsePattern.DISCARD, UsePattern.BANISH):
            card_types.append(
                _build_card_type(
                    CardAction.HEAL,
                    usage_pattern,
                    if_permanent=False,
                    color=color,
                )
            )

        for action in (CardAction.HAND_BUFF, CardAction.ECHO_BUFF):
            for usage_pattern in UsePattern:
                for if_permanent in (False, True):
                    card_types.append(
                        _build_card_type(
                            action,
                            usage_pattern,
                            if_permanent=if_permanent,
                            color=color,
                        )
                    )

    return tuple(card_types)


def _random_card_type() -> CardType:
    return random.choice(list_card_types())


def _slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-") or "card"


def _build_image(title: str) -> Image:
    image_id = uuid5(CARD_IMAGE_NAMESPACE, title.lower())
    return Image(
        id=image_id,
        title=title,
        file=f"cards/{_slugify(title)}.png",
    )


def generate_cards(count: int) -> list[Card]:
    titles = [
        "Gimli",
        "Legolas",
        "Aragorn",
        "Boromir",
        "Balin",
        "Dwalin",
        "Kili",
        "Fili",
        "Bifur",
        "Bofur",
        "Bombur",
        "Dori",
        "Nori",
        "Ori",
        "Gloin",
        "Oin",
        "Thorin",
        "Fireball",
        "Ice Bolt",
        "Shadow Strike",
        "Heal",
        "Lightning",
        "Curse",
        "Poison",
        "Dwarf",
        "Elf",
        "Human",
        "Orc",
        "Troll",
        "Goblin",
        "Ogre",
        "Wizard",
        "Warlock",
        "Sorcerer",
        "Knight",
        "Paladin",
        "Sword",
        "Axe",
        "Bow",
        "Staff",
        "Shield",
        "Wand",
        "Wolf",
        "Dragon",
        "Bear",
        "Lion",
        "Eagle",
        "Hawk",
        "Snake",
        "Scorpion",
    ]
    creatures = [
        "Giant",
        "Dragon",
        "Troll",
        "Goblin",
        "Ogre",
        "Wizard",
        "Warlock",
        "Sorcerer",
        "Knight",
        "Paladin",
        "Sword",
        "Axe",
        "Bow",
        "Staff",
        "Shield",
        "Wand",
        "Wolf",
        "Dragon",
        "Bear",
    ]

    cards: list[Card] = []
    for i in range(count):
        title = (
            titles[i]
            if i < len(titles)
            else f"{titles[i % len(titles)]} #{i // len(titles) + 1}"
        )
        card_type = _random_card_type()
        image = _build_image(title)
        cards.append(
            Card(
                id=uuid4(),
                title=title,
                creature=creatures[i % len(creatures)],
                image_id=image.id,
                power=random.randint(1, 5),
                echo=random.randint(0, 3),
                cost=random.randint(1, 5),
                cool_points=random.randint(0, 3),
                card_type_id=card_type.id,
                image=image,
            )
        )

    return cards
