from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from infrastructure.db.base import Base

if TYPE_CHECKING:
    pass


class CardTypeModel(Base):
    __tablename__ = "card_types"

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    action: Mapped[str] = mapped_column(String(200), nullable=False)
    usage_pattern: Mapped[str] = mapped_column(String(200), nullable=False)
    if_permanent: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    color: Mapped[str] = mapped_column(String(200), nullable=False, default="red")
    # card: Mapped["CardModel"] = relationship(
    #     "CardModel",
    #     back_populates="card_type",
    # )
