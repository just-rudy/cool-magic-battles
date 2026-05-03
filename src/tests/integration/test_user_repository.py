from uuid import uuid4

import pytest

from sqlalchemy.orm import Session

from domain.entities import User
from infrastructure.db.exceptions import EntityNotFoundError, EntityValidationError
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def test_save_and_get_user(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    user = User(id=uuid4(), username="alice")

    repo.save(user)
    loaded = repo.get(user.id)

    assert loaded.id == user.id
    assert loaded.username == "alice"


def test_update_user(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    user = User(id=uuid4(), username="alice")
    repo.save(user)

    user.username = "alice_new"
    repo.save(user)

    loaded = repo.get(user.id)
    assert loaded.username == "alice_new"


def test_delete_user(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    user = User(id=uuid4(), username="alice")
    repo.save(user)

    repo.delete(user.id)

    assert repo.exists(user.id) is False
    with pytest.raises(EntityNotFoundError):
        repo.get(user.id)


def test_save_user_with_empty_username_raises_error(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)

    with pytest.raises(EntityValidationError):
        repo.save(User(id=uuid4(), username="   "))
