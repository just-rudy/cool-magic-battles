from uuid import UUID

from sqlalchemy import CheckConstraint, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from domain.enums import UserRole
from infrastructure.db.base import Base


class UserModel(Base):
    __tablename__ = "users"
    __table_args__ = (
        UniqueConstraint("username", name="uq_user_username"),
        CheckConstraint(
            "role in ('guest', 'authenticated', 'player', 'moderator', 'master')",
            name="ck_users_role",
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    username: Mapped[str] = mapped_column(String(50), nullable=False)
    role: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=UserRole.AUTHENTICATED.value,
        server_default=UserRole.AUTHENTICATED.value,
    )
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
