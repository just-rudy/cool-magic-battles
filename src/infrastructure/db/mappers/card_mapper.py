from domain.entities.card import Card
from infrastructure.db.models.card_model import CardModel


class CardMapper:
    @staticmethod
    def to_domain(model: CardModel) -> Card:
        return Card(
            id=model.id,
            title=model.title,
            creature=model.creature,
            power=model.power,
            echo=model.echo,
            cost=model.cost,
            cool_points=model.cool_points,
        )

    @staticmethod
    def to_model(entity: Card) -> CardModel:
        return CardModel(
            id=entity.id,
            title=entity.title,
            creature=entity.creature,
            power=entity.power,
            echo=entity.echo,
            cost=entity.cost,
            cool_points=entity.cool_points,
        )
