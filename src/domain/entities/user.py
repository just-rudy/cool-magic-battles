from dataclasses import dataclass
from uuid import UUID

from domain.enums import UserRole


@dataclass
class User:
    id: UUID
    username: str
    role: UserRole = UserRole.AUTHENTICATED
    password_hash: str | None = None
