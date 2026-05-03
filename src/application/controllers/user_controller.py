from uuid import UUID, uuid4
from typing import Any

from domain.entities import User
from application.interfaces.user_repository import UserRepository


class UserController:
    def __init__(self, user_repository: UserRepository) -> None:
        self._user_repo = user_repository

    def register_user(self, username: str) -> User:
        user = User(id=uuid4(), username=username)
        self._user_repo.save(user)
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
