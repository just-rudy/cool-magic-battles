from uuid import UUID, uuid4
from typing import Any

from domain.entities import User
from application.interfaces.user_repository import UserRepository


class UserController:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

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

    def register_user(self, username: str) -> User:
        stripped = username.strip()
        if not stripped:
            raise ValueError("username must not be empty")

        if self._find_by_username(stripped) is not None:
            raise ValueError("username already taken")

        user = User(id=uuid4(), username=stripped)
        self._user_repo.save(user)
        return user

    def login_user(self, username: str) -> User:
        user = self._find_by_username(username)
        if user is None:
            raise ValueError(f"user '{username.strip()}' not found")
        return user

    def get_user_by_id(self, user_id: UUID) -> User:
        return self._user_repo.get(user_id)

    def show_user(self, user_id: UUID) -> dict[str, Any]:
        user = self._user_repo.get(user_id)
        return {"id": str(user.id), "username": user.username}

    def list_users(self) -> list[dict[str, Any]]:
        users = self._user_repo.list_all()
        return [
            {
                "id": str(user.id),
                "username": user.username,
            }
            for user in users
        ]
