from dataclasses import dataclass, field
from uuid import UUID, uuid4
from domain.entities.player import Player
from domain.entities.deck import Deck
from domain.enums import GameStatus


@dataclass
class Game:
    id: UUID
    host_id: UUID
    status: GameStatus = GameStatus.CREATED
    players: list[Player] = field(default_factory=list)
    current_turn: int = 0
    current_player_id: UUID | None = None
    market_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
    game_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
    banish_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
