"""MongoDB document models (TypedDict)."""
from .card_model import CardDocument, CardTypeEmbedded, ImageDocument
from .card_type_model import CardTypeDocument
from .game_model import (
    DeckDocument,
    GameDocument,
    PendingAttackDocument,
    PlayerDocument,
)
from .user_model import UserDocument

__all__ = [
    "UserDocument",
    "CardTypeDocument",
    "CardDocument",
    "ImageDocument",
    "CardTypeEmbedded",
    "GameDocument",
    "DeckDocument",
    "PlayerDocument",
    "PendingAttackDocument",
]
