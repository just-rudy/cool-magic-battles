from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from domain.entities import Card
from infrastructure.db.exceptions.validation_errors import EntityValidationError
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)


def test_save_and_get_card(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)
    card = Card(
        id=uuid4(),
        title="Zap",
        creature="wizard",
        power=2,
        echo=1,
        cost=3,
        cool_points=1,
    )

    repo.save(card)
    loaded = repo.get(card.id)

    assert loaded.id == card.id
    assert loaded.title == "Zap"
    assert loaded.cool_points == 1


def test_list_all_cards(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)
    repo.save(Card(id=uuid4(), title="Alpha", creature="elf"))
    repo.save(Card(id=uuid4(), title="Beta", creature="dwarf"))

    cards = repo.list_all()

    assert len(cards) == 2
    assert [card.title for card in cards] == ["Alpha", "Beta"]


def test_save_invalid_card_raises_error(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)

    with pytest.raises(EntityValidationError):
        repo.save(Card(id=uuid4(), title="", creature="wizard"))
