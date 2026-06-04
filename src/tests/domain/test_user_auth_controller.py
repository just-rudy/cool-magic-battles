from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from application.controllers.user_controller import UserController
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def _controller(session: Session) -> UserController:
    return UserController(SqlAlchemyUserRepository(session))


def test_register_and_login_with_password(session: Session) -> None:
    controller = _controller(session)
    user = controller.register_user("mage_alpha", "secret12")
    assert user.password_hash is not None

    logged_in = controller.login_user("mage_alpha", "secret12")
    assert logged_in.id == user.id

    with pytest.raises(ValueError, match="invalid password"):
        controller.login_user("mage_alpha", "wrong")


def test_register_rejects_short_password(session: Session) -> None:
    controller = _controller(session)
    with pytest.raises(ValueError, match="at least 6"):
        controller.register_user("short_pw", "12345")


def test_login_legacy_user_without_password_then_sets_password(session: Session) -> None:
    repo = SqlAlchemyUserRepository(session)
    from domain.entities import User

    legacy = User(id=uuid4(), username="legacy_mage")
    repo.save(legacy)

    controller = _controller(session)
    user = controller.login_user("legacy_mage", "newpass1")
    assert user.id == legacy.id
    assert user.password_hash is not None

    with pytest.raises(ValueError, match="invalid password"):
        controller.login_user("legacy_mage", "wrong")
