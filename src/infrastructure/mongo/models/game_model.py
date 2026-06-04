"""MongoDB document model for Game."""
from typing import TypedDict

from typing_extensions import NotRequired

from .card_model import CardDocument


class PendingAttackDocument(TypedDict):
    attacker_id: str
    defender_id: str
    damage: int


class DeckDocument(TypedDict):
    id: str
    type: str  # DeckType.value
    if_open: bool
    cards: list[CardDocument]


class PlayerDocument(TypedDict):
    id: str
    user_id: str
    nickname: str
    turn_order: int
    health: int
    base_echo: int
    cur_echo: int
    hand_size: int
    draw_deck: DeckDocument
    hand_deck: DeckDocument
    table_deck: DeckDocument
    discard_deck: DeckDocument


class GameDocument(TypedDict):
    _id: str
    host_user_id: str
    name: str
    status: str  # GameStatus.value
    cur_turn: int
    cur_player_id: str | None
    winner_id: str | None
    pending_attack: NotRequired[PendingAttackDocument | None]
    market_deck: DeckDocument
    game_deck: DeckDocument
    banish_deck: DeckDocument
    players: list[PlayerDocument]
