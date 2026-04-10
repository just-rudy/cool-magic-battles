from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from application.interfaces.user_repository import UserRepository
from domain.entities.user import User
from infrastructure.db.exceptions import (
    EntityNotFoundError,
    EntityValidationError,
    PersistenceError,
)
from infrastructure.db.mappers.user_mapper import UserMapper
from infrastructure.db.models.user_model import UserModel


class SqlAlchemyUserRepository(UserRepository):
    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, user: User) -> None:
        if not user.username.strip():
            raise EntityValidationError("err: uername must not be empty")

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
                "err: failed to save user: integrity constraint violated"
            ) from exc
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("err: failed to save user") from exc

    def get(self, user_id: UUID) -> User:
        model = self._session.get(UserModel, user_id)
        if model is None:
            raise EntityNotFoundError(f"err: user {user_id} not found")
        return UserMapper.to_domain(model)

    def delete(self, user_id: UUID) -> None:
        model = self._session.get(UserModel, user_id)
        if model is None:
            raise EntityNotFoundError(f"err: user {user_id} not found")

        try:
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("err: failed to delete user") from exc

    def exists(self, user_id: UUID) -> bool:
        return self._session.get(UserModel, user_id) is not None
