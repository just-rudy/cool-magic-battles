from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from domain.entities import Card, Image
from infrastructure.db.exceptions.validation_errors import EntityValidationError
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)


def make_image(title: str) -> Image:
    return Image(
        id=uuid4(),
        title=title,
        file=f"cards/{title.lower()}.png",
    )


def test_save_and_get_card(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)
    image = make_image("Zap")
    card = Card(
        id=uuid4(),
        title="Zap",
        creature="wizard",
        card_type_id=uuid4(),
        image_id=image.id,
        power=2,
        echo=1,
        cost=3,
        cool_points=1,
        image=image,
    )

    repo.save(card)
    loaded = repo.get(card.id)

    assert loaded.id == card.id
    assert loaded.title == "Zap"
    assert loaded.cool_points == 1
    assert loaded.image is not None
    assert loaded.image.file == "cards/zap.png"


def test_list_all_cards(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)
    alpha_image = make_image("Alpha")
    beta_image = make_image("Beta")
    repo.save(
        Card(
            id=uuid4(),
            title="Alpha",
            creature="elf",
            card_type_id=uuid4(),
            image_id=alpha_image.id,
            image=alpha_image,
        )
    )
    repo.save(
        Card(
            id=uuid4(),
            title="Beta",
            creature="dwarf",
            card_type_id=uuid4(),
            image_id=beta_image.id,
            image=beta_image,
        )
    )

    cards = repo.list_all()

    assert len(cards) == 2
    assert [card.title for card in cards] == ["Alpha", "Beta"]
    assert cards[0].image is not None


def test_save_invalid_card_raises_error(session: Session) -> None:
    repo = SqlAlchemyCardRepository(session)
    image = make_image("Wizard")

    with pytest.raises(EntityValidationError):
        repo.save(
            Card(
                id=uuid4(),
                title="",
                creature="wizard",
                card_type_id=uuid4(),
                image_id=image.id,
                image=image,
            )
        )
