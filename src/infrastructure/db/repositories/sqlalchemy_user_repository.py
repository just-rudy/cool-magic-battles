from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from application.interfaces.user_repository import UserRepository
from domain.entities import User
from infrastructure.db.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    PersistenceError,
)
from infrastructure.db.mappers.user_mapper import UserMapper
from infrastructure.db.models import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, user: User) -> None:
        if not user.username.strip():
            raise EntityValidationError("username must not be empty")

        try:
            model = self._session.get(UserModel, user.id)
            if model is None:
                model = UserMapper.to_model(user)
                self._session.add(model)
            else:
                model.username = user.username
            self._session.commit()
        except IntegrityError as exc:
            self._session.rollback()
            raise PersistenceError(
                "failed to save user: integrity constraint violated"
            ) from exc
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("failed to save user") from exc

    def get(self, user_id: UUID) -> User:
        model = self._session.get(UserModel, user_id)
        if model is None:
            raise EntityNotFoundError(f"user {user_id} not found")
        return UserMapper.to_domain(model)

    def delete(self, user_id: UUID) -> None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            raise EntityNotFoundError(f"user {user_id} not found")

        try:
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("failed to delete user") from exc

    def exists(self, user_id: UUID) -> bool:
        return self._session.get(UserModel, user_id) is not None

    def get_by_username(self, username: str) -> User | None:
        model = (
            self._session.query(UserModel)
            .filter(UserModel.username == username)
            .one_or_none()
        )
        if model is None:
            return None
        return UserMapper.to_domain(model)

    def list_all(self) -> list[User]:
        models = self._session.query(UserModel).all()
        return [UserMapper.to_domain(m) for m in models]
