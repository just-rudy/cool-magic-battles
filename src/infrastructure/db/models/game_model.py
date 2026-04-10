from uuid import UUID
from sqlalchemy import Uuid, Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.base import Base


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    host_user_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("users.id"), nullable=False
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    current_turn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    current_player_id: Mapped[UUID | None] = mapped_column(
        Uuid, ForeignKey("players.id"), nullable=True
    )
    # memos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # time_start: Mapped[str] = mapped_column(String(50), nullable=False)
    # time_end: Mapped[str | None] = mapped_column(String(50), nullable=True)
    # winner_id: Mapped[str | None] = mapped_column(nullable=True)
