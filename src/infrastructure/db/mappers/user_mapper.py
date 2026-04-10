from domain.entities.user import User
from infrastructure.db.models.user_model import UserModel


class UserMapper:
    @staticmethod
    def to_domain(model: UserModel) -> User:
        return User(
            id=model.id,
            username=model.username,
            # email=model.email,
        )

    @staticmethod
    def to_model(entity: User) -> UserModel:
        return UserModel(
            id=entity.id,
            username=entity.username,
            # email=entity.email,
        )
