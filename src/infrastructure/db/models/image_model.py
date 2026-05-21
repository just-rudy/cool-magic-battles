from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from infrastructure.db.base import Base

if TYPE_CHECKING:
    from infrastructure.db.models.card_model import CardModel


class ImageModel(Base):
    __tablename__ = "images"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    cards: Mapped[list["CardModel"]] = relationship(
        "CardModel",
        back_populates="image",
    )
