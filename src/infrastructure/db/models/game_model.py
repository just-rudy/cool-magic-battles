from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.deck_model import DeckModel
    from infrastructure.db.models.player_model import PlayerModel


class GameModel(Base):
    __tablename__ = "games"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    host_user_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, default="")
    status: Mapped[str] = mapped_column(String(50), nullable=False)
    cur_turn: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    cur_player_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    winner_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("players.id", use_alter=True, name="fk_games_winner_id_players"),
        nullable=True,
    )
    # pending attack fields (nullable — атаки может не быть)
    pending_attacker_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    pending_defender_id: Mapped[UUID | None] = mapped_column(
        Uuid(as_uuid=True), nullable=True
    )
    pending_damage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    players: Mapped[list["PlayerModel"]] = relationship(
        "PlayerModel",
        back_populates="game",
        cascade="all, delete-orphan",
        foreign_keys="PlayerModel.game_id",
    )
    decks: Mapped[list["DeckModel"]] = relationship(
        "DeckModel",
        back_populates="game",
        cascade="all, delete-orphan",
    )
