from domain.entities import User
from domain.enums import UserRole
from infrastructure.db.models import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            role=UserRole(model.role),
            password_hash=model.password_hash,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            role=entity.role.value,
            password_hash=entity.password_hash,
        )
