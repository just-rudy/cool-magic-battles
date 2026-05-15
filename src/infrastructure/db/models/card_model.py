from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.deck_card_model import DeckCardModel


class CardModel(Base):
    __tablename__ = "cards"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    creature: Mapped[str] = mapped_column(String(100), nullable=False)
    power: Mapped[int] = mapped_column(Integer, nullable=False, default=2)
    echo: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    cost: Mapped[int] = mapped_column(Integer, nullable=False, default=3)
    cool_points: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    deck_cards: Mapped[list["DeckCardModel"]] = relationship(
        "DeckCardModel",
        back_populates="card",
    )
