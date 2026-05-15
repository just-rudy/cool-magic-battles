import random
from uuid import uuid4

from domain.entities import Card


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
        cards.append(
            Card(
                id=uuid4(),
                title=title,
                creature=creatures[i % len(creatures)],
                power=random.randint(1, 5),
                echo=random.randint(0, 3),
                cost=random.randint(1, 5),
                cool_points=random.randint(0, 3),
            )
        )

    return cards
