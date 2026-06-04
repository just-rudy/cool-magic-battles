"""Tests for MongoCardRepository."""
from uuid import uuid4

import pytest

from domain.entities import Card
from domain.entities.card_type import CardType
from domain.entities.image import Image
from domain.enums import CardAction, UsePattern
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.mongo.repositories.mongo_card_repository import MongoCardRepository


@pytest.fixture
def repo(mongo_db):
    return MongoCardRepository(mongo_db)


def _make_card(title="Aragorn", power=3) -> Card:
    image = Image(id=uuid4(), title=title, file=f"cards/{title.lower()}.png")
    card_type = CardType(
        id=uuid4(), action=CardAction.ATTACK, usage_pattern=UsePattern.REG, color="red"
    )
    return Card(
        id=uuid4(),
        title=title,
        creature="Human",
        card_type_id=card_type.id,
        image_id=image.id,
        power=power,
        echo=1,
        cost=3,
        cool_points=1,
        image=image,
        card_type=card_type,
    )


def test_save_and_get(repo):
    card = _make_card()
    repo.save(card)

    result = repo.get(card.id)
    assert result.id == card.id
    assert result.title == "Aragorn"
    assert result.power == 3


def test_get_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.get(uuid4())


def test_save_updates_existing(repo):
    card = _make_card(power=2)
    repo.save(card)

    card.power = 5
    repo.save(card)

    result = repo.get(card.id)
    assert result.power == 5


def test_delete(repo):
    card = _make_card()
    repo.save(card)
    repo.delete(card.id)

    with pytest.raises(EntityNotFoundError):
        repo.get(card.id)


def test_delete_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.delete(uuid4())


def test_exists(repo):
    card = _make_card()
    repo.save(card)
    assert repo.exists(card.id) is True
    assert repo.exists(uuid4()) is False


def test_list_all_sorted_by_title(repo):
    cards = [_make_card(title=t) for t in ["Gimli", "Aragorn", "Legolas"]]
    for c in cards:
        repo.save(c)

    result = repo.list_all()
    titles = [c.title for c in result]
    assert titles == sorted(titles)


def test_find_by_title(repo):
    card = _make_card(title="Boromir")
    repo.save(card)

    result = repo.find_by_title("Boromir")
    assert result is not None
    assert result.id == card.id


def test_find_by_title_returns_none(repo):
    assert repo.find_by_title("Nobody") is None


def test_card_image_and_type_preserved(repo):
    card = _make_card()
    repo.save(card)

    result = repo.get(card.id)
    assert result.image is not None
    assert result.image.file == "cards/aragorn.png"
    assert result.card_type is not None
    assert result.card_type.action == CardAction.ATTACK
