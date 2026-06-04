from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session, selectinload

from application.interfaces.card_repository import CardRepository
from domain.entities import Card
from infrastructure.db.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    PersistenceError,
)
from infrastructure.db.mappers.card_mapper import CardMapper
from infrastructure.db.mappers.image_mapper import ImageMapper
from infrastructure.db.models import CardModel, ImageModel


class SqlAlchemyCardRepository(CardRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def _sync_image(self, card: Card) -> None:
        if card.image is None:
            raise EntityValidationError("card image must be provided")
        if card.image.id != card.image_id:
            raise EntityValidationError("card image id must match image.id")

        image_model = self._session.get(ImageModel, card.image_id)
        if image_model is None:
            image_model = ImageMapper.to_model(card.image)
            self._session.add(image_model)
            return

        image_model.title = card.image.title
        image_model.file = card.image.file

    def save(self, card: Card) -> None:
        if not card.title.strip():
            raise EntityValidationError("card title must not be empty")
        if not card.creature.strip():
            raise EntityValidationError("card creature must not be empty")
        if card.cost < 0:
            raise EntityValidationError("card cost must be non-negative")
        try:
            self._sync_image(card)
            model = self._session.get(CardModel, card.id)
            if model is None:
                model = CardMapper.to_model(card)
                self._session.add(model)
            else:
                model.title = card.title
                model.creature = card.creature
                model.card_type_id = card.card_type_id
                model.image_id = card.image_id
                model.power = card.power
                model.echo = card.echo
                model.cost = card.cost
                model.cool_points = card.cool_points
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise PersistenceError(
                "failed to save card - integrity constraint violated"
            ) from exc
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("failed to save card") from exc

    def get(self, card_id: UUID) -> Card:
        model = (
            self._session.query(CardModel)
            .options(
                selectinload(CardModel.image),
                selectinload(CardModel.card_type),
            )
            .filter(CardModel.id == card_id)
            .one_or_none()
        )
        if model is None:
            raise EntityNotFoundError(f"card {card_id} not found")
        return CardMapper.to_domain(model)

    def delete(self, card_id: UUID) -> None:
        model = self._session.get(CardModel, card_id)
        if model is None:
            raise EntityNotFoundError(f"card {card_id} not found")

        try:
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError(f"failed to delete card {card_id}") from exc

    def exists(self, card_id: UUID) -> bool:
        model = self._session.get(CardModel, card_id)
        return model is not None

    def list_all(self) -> list[Card]:
        models = (
            self._session.query(CardModel)
            .options(
                selectinload(CardModel.image),
                selectinload(CardModel.card_type),
            )
            .order_by(CardModel.title.asc())
            .all()
        )
        return [CardMapper.to_domain(model) for model in models]

    def find_by_title(self, title: str) -> Card | None:
        model = (
            self._session.query(CardModel)
            .options(
                selectinload(CardModel.image),
                selectinload(CardModel.card_type),
            )
            .filter(CardModel.title == title)
            .one_or_none()
        )

        if model is None:
            return None

        return CardMapper.to_domain(model)
