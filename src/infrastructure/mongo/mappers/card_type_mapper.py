"""Mapper: CardType entity ↔ CardTypeDocument."""
from uuid import UUID

from domain.card_colors import color_for_action
from domain.entities import CardType
from domain.enums import CardAction, UsePattern
from infrastructure.mongo.models.card_type_model import CardTypeDocument


class MongoCardTypeMapper:
    @staticmethod
    def to_document(ct: CardType) -> CardTypeDocument:
        return CardTypeDocument(
            _id=str(ct.id),
            action=ct.action.value,
            usage_pattern=ct.usage_pattern.value,
            if_permanent=ct.if_permanent,
            color=color_for_action(ct.action),
        )

    @staticmethod
    def to_entity(doc: CardTypeDocument) -> CardType:
        action = CardAction(doc["action"])
        return CardType(
            id=UUID(doc["_id"]),
            action=action,
            usage_pattern=UsePattern(doc["usage_pattern"]),
            if_permanent=doc.get("if_permanent", False),
            color=color_for_action(action),
        )
