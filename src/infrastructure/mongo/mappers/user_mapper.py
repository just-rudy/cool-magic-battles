"""Mapper: User entity ↔ UserDocument."""
from uuid import UUID

from domain.entities import User
from domain.enums import UserRole
from infrastructure.mongo.models.user_model import UserDocument


class MongoUserMapper:
    @staticmethod
    def to_document(user: User) -> UserDocument:
        return UserDocument(
            _id=str(user.id),
            username=user.username,
            role=user.role.value,
        )

    @staticmethod
    def to_entity(doc: UserDocument) -> User:
        return User(
            id=UUID(doc["_id"]),
            username=doc["username"],
            role=UserRole(doc.get("role", UserRole.AUTHENTICATED.value)),
        )
