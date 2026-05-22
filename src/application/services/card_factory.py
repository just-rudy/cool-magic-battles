import random
import re
from dataclasses import dataclass
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
        # ATTACK: reg
        card_types.append(
            _build_card_type(CardAction.ATTACK, UsePattern.REG, if_permanent=False, color=color)
        )

        # DRAW: reg
        card_types.append(
            _build_card_type(CardAction.DRAW, UsePattern.REG, if_permanent=False, color=color)
        )

        # DEF: discard, on_top
        for usage_pattern in (UsePattern.DISCARD, UsePattern.ON_TOP):
            card_types.append(
                _build_card_type(CardAction.DEF, usage_pattern, if_permanent=False, color=color)
            )

        # HEAL: reg, discard
        for usage_pattern in (UsePattern.REG, UsePattern.DISCARD):
            card_types.append(
                _build_card_type(CardAction.HEAL, usage_pattern, if_permanent=False, color=color)
            )

        # HAND_BUFF, ECHO_BUFF: только banish
        for action in (CardAction.HAND_BUFF, CardAction.ECHO_BUFF):
            card_types.append(
                _build_card_type(action, UsePattern.BANISH, if_permanent=False, color=color)
            )

    return tuple(card_types)


# ─── Параметры баланса ────────────────────────────────────────────────────────

@dataclass
class CardStats:
    """Диапазоны статов для конкретного типа карты."""
    power_range: tuple[int, int]
    echo_range: tuple[int, int]
    cost_range: tuple[int, int]
    cool_points_range: tuple[int, int]


CARD_STATS: dict[CardAction, CardStats] = {
    # Атака: сила 1–5, встречается часто
    CardAction.ATTACK: CardStats(
        power_range=(1, 5),
        echo_range=(0, 2),
        cost_range=(2, 5),
        cool_points_range=(0, 2),
    ),
    # Защита: сила 1–4, встречается реже
    CardAction.DEF: CardStats(
        power_range=(1, 4),
        echo_range=(0, 2),
        cost_range=(2, 5),
        cool_points_range=(0, 2),
    ),
    # Добор: не больше 3 карт
    CardAction.DRAW: CardStats(
        power_range=(1, 3),
        echo_range=(0, 2),
        cost_range=(2, 4),
        cool_points_range=(0, 1),
    ),
    # Лечение: не больше 3 хп
    CardAction.HEAL: CardStats(
        power_range=(1, 3),
        echo_range=(0, 2),
        cost_range=(2, 4),
        cool_points_range=(0, 1),
    ),
    # Бафф руки: сила только 1, редкие
    CardAction.HAND_BUFF: CardStats(
        power_range=(1, 1),
        echo_range=(0, 1),
        cost_range=(3, 5),
        cool_points_range=(1, 3),
    ),
    # Бафф эхо: сила только 1, редкие
    CardAction.ECHO_BUFF: CardStats(
        power_range=(1, 1),
        echo_range=(0, 1),
        cost_range=(3, 5),
        cool_points_range=(1, 3),
    ),
}

# Веса для выбора типа карты (чем больше — тем чаще встречается)
# ATTACK: 40%, DEF: 20%, DRAW: 20%, HEAL: 10%, HAND_BUFF: 5%, ECHO_BUFF: 5%
ACTION_WEIGHTS: dict[CardAction, int] = {
    CardAction.ATTACK: 40,
    CardAction.DEF: 20,
    CardAction.DRAW: 20,
    CardAction.HEAL: 10,
    CardAction.HAND_BUFF: 5,
    CardAction.ECHO_BUFF: 5,
}


def _random_card_type() -> CardType:
    """Выбирает тип карты с учётом весов баланса."""
    all_types = list_card_types()

    # Группируем по action
    by_action: dict[CardAction, list[CardType]] = {}
    for ct in all_types:
        by_action.setdefault(ct.action, []).append(ct)

    # Выбираем action по весам
    actions = list(ACTION_WEIGHTS.keys())
    weights = [ACTION_WEIGHTS[a] for a in actions]
    chosen_action = random.choices(actions, weights=weights, k=1)[0]

    # Выбираем конкретный тип из доступных для этого action
    return random.choice(by_action[chosen_action])


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
        stats = CARD_STATS[card_type.action]
        image = _build_image(title)
        cards.append(
            Card(
                id=uuid4(),
                title=title,
                creature=creatures[i % len(creatures)],
                image_id=image.id,
                power=random.randint(*stats.power_range),
                echo=random.randint(*stats.echo_range),
                cost=random.randint(*stats.cost_range),
                cool_points=random.randint(*stats.cool_points_range),
                card_type_id=card_type.id,
                image=image,
            )
        )

    return cards
