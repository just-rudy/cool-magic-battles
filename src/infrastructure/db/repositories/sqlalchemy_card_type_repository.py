from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from application.interfaces.card_type_repository import CardTypeRepository
from domain.card_colors import color_for_action
from domain.entities import CardType
from domain.enums import CardAction, UsePattern
from infrastructure.db.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    PersistenceError,
)
from infrastructure.db.mappers.card_type_mapper import CardTypeMapper
from infrastructure.db.models import CardTypeModel


class SqlAlchemyCardTypeRepository(CardTypeRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, card_type: CardType) -> None:
        allowed_actions = ", ".join(f"'{action.value}'" for action in CardAction)
        allowed_patterns = ", ".join(f"'{pattern.value}'" for pattern in UsePattern)

        if not card_type.action.strip():
            raise EntityValidationError("card type action must not be empty")
        if card_type.action not in list(CardAction):
            raise EntityValidationError(
                f"card type action must be one of {allowed_actions}"
            )
        if not card_type.usage_pattern.strip():
            raise EntityValidationError("card type usage pattern must not be empty")
        if card_type.usage_pattern not in list(UsePattern):
            raise EntityValidationError(
                f"card type usage pattern must be one of {allowed_patterns}"
            )
        try:
            model = self._session.get(CardTypeModel, card_type.id)
            resolved_color = color_for_action(card_type.action)
            if model is None:
                card_type.color = resolved_color
                model = CardTypeMapper.to_model(card_type)
                self._session.add(model)
            else:
                model.action = card_type.action.value
                model.usage_pattern = card_type.usage_pattern.value
                model.if_permanent = card_type.if_permanent
                model.color = resolved_color
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise PersistenceError(
                "failed to save card type - integrity constraint violated"
            ) from exc
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("failed to save card type") from exc

    def get(self, card_type_id: UUID) -> CardType:
        model = self._session.get(CardTypeModel, card_type_id)
        if model is None:
            raise EntityNotFoundError(f"card type {card_type_id} not found")
        return CardTypeMapper.to_domain(model)

    def delete(self, card_type_id: UUID) -> None:
        model = self._session.get(CardTypeModel, card_type_id)
        if model is None:
            raise EntityNotFoundError(f"card type {card_type_id} not found")

        try:
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError(f"failed to delete card {card_type_id}") from exc

    def exists(self, card_type_id: str) -> bool:
        model = self._session.get(CardTypeModel, card_type_id)
        return model is not None

    def list_all(self) -> list[CardType]:
        models = (
            self._session.query(CardTypeModel)
            .order_by(CardTypeModel.action.asc())
            .all()
        )
        return [CardTypeMapper.to_domain(model) for model in models]

    def find_by_title(self, title: str) -> CardType | None:
        model = (
            self._session.query(CardTypeModel)
            .filter(CardTypeModel.action == title)
            .one_or_none()
        )

        if model is None:
            return None

        return CardTypeMapper.to_domain(model)
