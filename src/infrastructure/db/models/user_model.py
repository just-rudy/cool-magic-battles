from uuid import UUID
from sqlalchemy import Uuid, String
from sqlalchemy.orm import Mapped, mapped_column
from infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(Uuid, primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    # email: Mapped[str] = mapped_column(String(100), nullable=False)
