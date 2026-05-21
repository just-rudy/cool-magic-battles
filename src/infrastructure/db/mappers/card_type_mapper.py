from domain.entities import CardType
from domain.enums import CardAction, UsePattern
from infrastructure.db.models import CardTypeModel


class CardTypeMapper:
    @staticmethod
    def to_domain(model: CardTypeModel) -> CardType:
        return CardType(
            id=model.id,
            action=CardAction(model.action),
            usage_pattern=UsePattern(model.usage_pattern),
            if_permanent=model.if_permanent,
            color=model.color,
        )

    @staticmethod
    def to_model(entity: CardType) -> CardTypeModel:
        return CardTypeModel(
            id=entity.id,
            action=entity.action.value,
            usage_pattern=entity.usage_pattern.value,
            if_permanent=entity.if_permanent,
            color=entity.color,
        )
