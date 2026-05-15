from dataclasses import dataclass, field
from uuid import UUID, uuid4

from .player import Player
from .deck import Deck
from domain.enums import GameStatus


@dataclass
class Game:
    id: UUID
    host_user_id: UUID
    status: GameStatus = GameStatus.CREATED
    players: list[Player] = field(default_factory=list)
    cur_turn: int = 0
    cur_player_id: UUID | None = None
    winner_id: UUID | None = None
    market_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
    game_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
    banish_deck: Deck = field(default_factory=lambda: Deck(id=uuid4()))
