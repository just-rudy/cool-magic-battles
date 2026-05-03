from uuid import UUID
from sqlalchemy import Boolean, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base
from domain.enums import DeckType


class DeckModel(Base):
    __tablename__ = "decks"
    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    type: Mapped[str] = mapped_column(String(50), nullable=False, default=DeckType.DRAW)
    game_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("games.id"), nullable=True
    )
    player_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("players.id"), nullable=True
    )
    if_open: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
