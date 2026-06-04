"""MongoDB document model for Card."""
from typing import TypedDict

from typing_extensions import NotRequired


class ImageDocument(TypedDict):
    id: str
    title: str
    file: str | None


class CardTypeEmbedded(TypedDict):
    id: str
    action: str
    usage_pattern: str
    if_permanent: bool
    color: str


class CardDocument(TypedDict):
    _id: str
    title: str
    creature: str
    card_type_id: str
    image_id: str
    power: int
    echo: int
    cost: int
    cool_points: int
    image: NotRequired[ImageDocument]
    card_type: NotRequired[CardTypeEmbedded]
