from dataclasses import dataclass
from uuid import UUID

from .card_type import CardType
from .image import Image


@dataclass
class Card:
    id: UUID
    title: str
    creature: str
    card_type_id: UUID
    image_id: UUID
    power: int = 1  # effect power
    echo: int = 1  # card buying currency
    cost: int = 3  # card cost in echo
    cool_points: int = 0
    image: Image | None = None
    card_type: CardType | None = None
