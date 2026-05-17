from dataclasses import dataclass, field
from uuid import UUID

from domain.enums import DeckType

from .card import Card


@dataclass
class Deck:
    id: UUID
    # game_id: UUID | None = None
    # player_id: UUID | None = None  # if it's a game deck, player_id is None
    type: DeckType = DeckType.DECK
    if_open: bool = False
    # cards will be moved later, here for simplicity
    cards: list[Card] = field(default_factory=list)
