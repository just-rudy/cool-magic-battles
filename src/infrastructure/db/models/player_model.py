from uuid import UUID
from sqlalchemy import Uuid, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.base import Base


class PlayerModel(Base):
    __tablename__ = "players"
    __table_args__ = (
        UniqueConstraint("game_id", "user_id", name="uq_players_game_user"),
    )

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    game_id: Mapped[UUID] = mapped_column(
        Uuid, ForeignKey("games.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[UUID] = mapped_column(Uuid, ForeignKey("users.id"), nullable=False)
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)
    turn_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    health: Mapped[int] = mapped_column(Integer, nullable=False, default=20)
    base_echo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cur_echo: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    hand_size: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    # memos: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    # color: Mapped[str] = mapped_column(String(20), nullable=False)
