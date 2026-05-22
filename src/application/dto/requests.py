# requests.py

from uuid import UUID

from pydantic import BaseModel


class CreateGameRequest(BaseModel):
    host_user_id: UUID


class JoinGameRequest(BaseModel):
    user_id: UUID


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
