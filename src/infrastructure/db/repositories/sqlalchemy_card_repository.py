from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session
from domain.entities.card import Card
from application.interfaces.card_repository import CardRepository
from infrastructure.db.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    PersistenceError,
)
from infrastructure.db.mappers.card_mapper import CardMapper
from infrastructure.db.models.card_model import CardModel


class SQLAlchemyCardRepository(CardRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, card: Card) -> None:
        if not card.title.strip():
            raise EntityValidationError("err: card title must not be empty")
        if not card.creature.strip():
            raise EntityValidationError("err: card creature must not be empty")
        if card.cost < 0:
            raise EntityValidationError("err: card cost must be non-negative")
        try:
            model = self._session.get(CardModel, card.id)
            if model is None:
                model = CardMapper.to_model(card)
                self._session.add(model)
            else:
                model.title = card.title
                model.creature = card.creature
                model.power = card.power
                model.echo = card.echo
                model.cost = card.cost
                model.cool_points = card.cool_points
                self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise PersistenceError(
                "err: failed to save card - integrity constraint violated"
            ) from exc
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("err: failed to save card") from exc

    def get(self, card_id: UUID) -> Card:
        model = self._session.get(CardModel, card_id)
        if model is None:
            raise EntityNotFoundError(f"err: card {card_id} not found")
        return CardMapper.to_domain(model)

    def delete(self, card_id: UUID) -> None:
        model = self._session.get(CardModel, card_id)
        if model is None:
            raise EntityNotFoundError(f"err: card {card_id} not found")

        try:
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError(f"err: failed to delete card {card_id}") from exc

    def exists(self, card_id: UUID) -> bool:
        model = self._session.get(CardModel, card_id)
        return model is not None

    def list_all(self) -> list[Card]:
        models = self._session.query(CardModel).order_by(CardModel.id).all()
        return [CardMapper.to_domain(model) for model in models]
