from domain.entities import Card
from infrastructure.db.mappers.card_type_mapper import CardTypeMapper
from infrastructure.db.mappers.image_mapper import ImageMapper
from infrastructure.db.models import CardModel


class CardMapper:
    @staticmethod
    def to_domain(model: CardModel) -> Card:
        return Card(
            id=model.id,
            title=model.title,
            creature=model.creature,
            card_type_id=model.card_type_id,
            image_id=model.image_id,
            power=model.power,
            echo=model.echo,
            cost=model.cost,
            cool_points=model.cool_points,
            image=(
                ImageMapper.to_domain(model.image)
                if model.image is not None
                else None
            ),
            card_type=(
                CardTypeMapper.to_domain(model.card_type)
                if model.card_type is not None
                else None
            ),
        )

    @staticmethod
    def to_model(entity: Card) -> CardModel:
        return CardModel(
            id=entity.id,
            title=entity.title,
            creature=entity.creature,
            card_type_id=entity.card_type_id,
            image_id=entity.image_id,
            power=entity.power,
            echo=entity.echo,
            cost=entity.cost,
            cool_points=entity.cool_points,
        )
