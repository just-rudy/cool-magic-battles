from uuid import UUID, uuid4

from sqlalchemy import ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base


class DeckCardModel(Base):
    __tablename__ = "deck_cards"
    __table_args__ = (UniqueConstraint("deck_id", "position", name="uq_deck_position"),)

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    deck_id: Mapped[UUID] = mapped_column(ForeignKey("decks.id"), nullable=False)
    card_id: Mapped[UUID] = mapped_column(ForeignKey("cards.id"), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
