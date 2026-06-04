"""Mapper: Card entity ↔ CardDocument."""
from uuid import UUID

from domain.card_colors import color_for_action
from domain.entities import Card
from domain.entities.card_type import CardType
from domain.entities.image import Image
from domain.enums import CardAction, UsePattern
from infrastructure.mongo.models.card_model import (
    CardDocument,
    CardTypeEmbedded,
    ImageDocument,
)


class MongoCardMapper:
    @staticmethod
    def _image_to_doc(image: Image) -> ImageDocument:
        return ImageDocument(
            id=str(image.id),
            title=image.title,
            file=image.file,
        )

    @staticmethod
    def _image_from_doc(doc: ImageDocument) -> Image:
        return Image(
            id=UUID(doc["id"]),
            title=doc["title"],
            file=doc.get("file"),
        )

    @staticmethod
    def _card_type_to_doc(ct: CardType) -> CardTypeEmbedded:
        return CardTypeEmbedded(
            id=str(ct.id),
            action=ct.action.value,
            usage_pattern=ct.usage_pattern.value,
            if_permanent=ct.if_permanent,
            color=color_for_action(ct.action),
        )

    @staticmethod
    def _card_type_from_doc(doc: CardTypeEmbedded) -> CardType:
        action = CardAction(doc["action"])
        return CardType(
            id=UUID(doc["id"]),
            action=action,
            usage_pattern=UsePattern(doc["usage_pattern"]),
            if_permanent=doc.get("if_permanent", False),
            color=color_for_action(action),
        )

    @staticmethod
    def to_document(card: Card) -> CardDocument:
        doc = CardDocument(
            _id=str(card.id),
            title=card.title,
            creature=card.creature,
            card_type_id=str(card.card_type_id),
            image_id=str(card.image_id),
            power=card.power,
            echo=card.echo,
            cost=card.cost,
            cool_points=card.cool_points,
        )
        if card.image is not None:
            doc["image"] = MongoCardMapper._image_to_doc(card.image)
        if card.card_type is not None:
            doc["card_type"] = MongoCardMapper._card_type_to_doc(card.card_type)
        return doc

    @staticmethod
    def to_entity(doc: CardDocument) -> Card:
        image = (
            MongoCardMapper._image_from_doc(doc["image"])
            if "image" in doc
            else None
        )
        card_type = (
            MongoCardMapper._card_type_from_doc(doc["card_type"])
            if "card_type" in doc
            else None
        )
        return Card(
            id=UUID(doc["_id"]),
            title=doc["title"],
            creature=doc["creature"],
            card_type_id=UUID(doc["card_type_id"]),
            image_id=UUID(doc["image_id"]),
            power=doc.get("power", 1),
            echo=doc.get("echo", 1),
            cost=doc.get("cost", 3),
            cool_points=doc.get("cool_points", 0),
            image=image,
            card_type=card_type,
        )
