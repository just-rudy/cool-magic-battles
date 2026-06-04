# requests.py

from uuid import UUID

from pydantic import BaseModel


class CreateGameRequest(BaseModel):
    host_user_id: UUID
    name: str | None = None


class JoinGameRequest(BaseModel):
    user_id: UUID


class JoinGameByRefRequest(BaseModel):
    user_id: UUID
    game_ref: str


class PlayCardRequest(BaseModel):
    player_id: UUID
    card_id: UUID
    target_id: UUID | None = None


class BuyCardRequest(BaseModel):
    player_id: UUID
    card_id: UUID


class EndTurnRequest(BaseModel):
    player_id: UUID


class DefendRequest(BaseModel):
    player_id: UUID
    card_id: UUID


class FinishGameRequest(BaseModel):
    player_id: UUID


class UpdateCardImageRequest(BaseModel):
    title: str | None = None
    filename: str
    content_base64: str
    content_type: str = "application/octet-stream"


class CreateCardRequest(BaseModel):
    title: str
    creature: str
    card_type_id: UUID
    power: int = 1
    echo: int = 1
    cost: int = 3
    cool_points: int = 0


class UpdateCardRequest(BaseModel):
    title: str
    creature: str
    card_type_id: UUID
    power: int
    echo: int
    cost: int
    cool_points: int
