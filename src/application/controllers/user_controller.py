import re
from typing import Any
from uuid import UUID, uuid4

from application.interfaces.user_repository import UserRepository
from domain.entities import User
from domain.enums import UserRole
from infrastructure.shared.passwords import hash_password, verify_password

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,30}$")


class UserController:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    def _validate_username(self, username: str) -> str:
        stripped = username.strip()
        if not USERNAME_PATTERN.fullmatch(stripped):
            raise ValueError(
                "username must be 3-30 characters: Latin letters, digits, underscore"
            )
        return stripped

    def _find_by_username(self, username: str) -> User | None:
        stripped = username.strip()
        if not stripped:
            return None

        user = self._user_repo.get_by_username(stripped)
        if user is not None:
            return user

        lowered = stripped.lower()
        for candidate in self._user_repo.list_all():
            if candidate.username.lower() == lowered:
                return candidate

        return None

    def register_user(
        self,
        username: str,
        password: str,
        role: UserRole = UserRole.AUTHENTICATED,
    ) -> User:
        name = self._validate_username(username)
        if len(password) < 6:
            raise ValueError("password must be at least 6 characters")
        if role == UserRole.GUEST:
            raise ValueError("guest is not a persistent user role")

        if self._find_by_username(name) is not None:
            raise ValueError("username already taken")

        user = User(
            id=uuid4(),
            username=name,
            role=role,
            password_hash=hash_password(password),
        )
        self._user_repo.save(user)
        return user

    def login_user(self, username: str, password: str | None = None) -> User:
        name = username.strip()
        if not name:
            raise ValueError("username must not be empty")

        user = self._find_by_username(name)
        if user is None:
            raise ValueError(f"user '{name}' not found")

        if user.password_hash:
            if not password:
                raise ValueError("password is required")
            if not verify_password(password, user.password_hash):
                raise ValueError("invalid password")
        elif password:
            user.password_hash = hash_password(password)
            self._user_repo.save(user)

        return user

    def get_user_by_id(self, user_id: UUID) -> User:
        return self._user_repo.get(user_id)

    def show_user(self, user_id: UUID) -> dict[str, Any]:
        user = self._user_repo.get(user_id)
        return {
            "id": str(user.id),
            "username": user.username,
            "role": user.role.value,
            "has_password": user.password_hash is not None,
        }

    def list_users(self) -> list[dict[str, Any]]:
        users = self._user_repo.list_all()
        return [
            {
                "id": str(user.id),
                "username": user.username,
                "role": user.role.value,
            }
            for user in users
        ]

    def update_user_role(self, user_id: UUID, role: UserRole) -> User:
        if role == UserRole.GUEST:
            raise ValueError("guest is not a persistent user role")

        user = self._user_repo.get(user_id)
        user.role = role
        self._user_repo.save(user)
        return user

    def delete_user(self, user_id: UUID) -> None:
        self._user_repo.delete(user_id)
