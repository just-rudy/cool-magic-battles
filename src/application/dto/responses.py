# responses.py

from uuid import UUID

from pydantic import BaseModel


class ImageResponse(BaseModel):
    id: UUID
    title: str
    file: str | None
    url: str | None = None


class CardTypeResponse(BaseModel):
    id: UUID
    action: str
    usage_pattern: str
    color: str


class CardResponse(BaseModel):
    id: UUID
    title: str
    creature: str
    image_id: UUID
    image: ImageResponse | None
    power: int
    echo: int
    cost: int
    cool_points: int
    card_type: CardTypeResponse | None = None


class PlayerResponse(BaseModel):
    id: UUID
    user_id: UUID
    nickname: str

    turn_order: int
    health: int

    base_echo: int
    cur_echo: int

    hand_size: int

    hand: list[CardResponse]
    table: list[CardResponse]
    discard: list[CardResponse]

    draw_count: int
    cool_points: int
    cards_count: int


class WinnerResponse(BaseModel):
    player_id: UUID
    nickname: str
    cool_points: int
    cards_count: int


class PendingAttackResponse(BaseModel):
    attacker_id: UUID
    defender_id: UUID
    damage: int


class GameResponse(BaseModel):
    id: UUID
    status: str

    cur_turn: int
    cur_player_id: UUID | None
    winner: WinnerResponse | None

    players: list[PlayerResponse]

    market: list[CardResponse]

    banish_count: int
    deck_count: int
    
    pending_attack: PendingAttackResponse | None = None


class UserResponse(BaseModel):
    id: UUID
    username: str


class DeckResponse(BaseModel):
    id: UUID
    type: str
    cards: list[CardResponse]
