"""MongoDB implementation of UserRepository."""
from typing import Any
from uuid import UUID

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from application.interfaces.user_repository import UserRepository
from domain.entities import User
from domain.enums import UserRole
from infrastructure.db.exceptions import EntityNotFoundError, PersistenceError


def _to_doc(user: User) -> dict[str, Any]:
    doc: dict[str, Any] = {
        "_id": str(user.id),
        "username": user.username,
        "role": user.role.value,
    }
    if user.password_hash is not None:
        doc["password_hash"] = user.password_hash
    return doc


def _from_doc(doc: dict[str, Any]) -> User:
    return User(
        id=UUID(doc["_id"]),
        username=doc["username"],
        role=UserRole(doc.get("role", UserRole.AUTHENTICATED.value)),
        password_hash=doc.get("password_hash"),
    )


class MongoUserRepository(UserRepository):
    COLLECTION = "users"

    def __init__(self, db: Database) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]
        # Уникальный индекс по username
        self._col.create_index("username", unique=True, background=True)

    def save(self, user: User) -> None:
        doc = _to_doc(user)
        try:
            self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        except DuplicateKeyError as exc:
            raise PersistenceError(
                "failed to save user: username already exists"
            ) from exc
        except PyMongoError as exc:
            raise PersistenceError("failed to save user") from exc

    def get(self, user_id: UUID) -> User:
        doc = self._col.find_one({"_id": str(user_id)})
        if doc is None:
            raise EntityNotFoundError(f"user {user_id} not found")
        return _from_doc(doc)

    def delete(self, user_id: UUID) -> None:
        result = self._col.delete_one({"_id": str(user_id)})
        if result.deleted_count == 0:
            raise EntityNotFoundError(f"user {user_id} not found")

    def exists(self, user_id: UUID) -> bool:
        return self._col.count_documents({"_id": str(user_id)}, limit=1) > 0

    def get_by_username(self, username: str) -> User | None:
        doc = self._col.find_one({"username": username})
        if doc is None:
            return None
        return _from_doc(doc)

    def list_all(self) -> list[User]:
        return [_from_doc(doc) for doc in self._col.find()]
