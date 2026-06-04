"""Tests for MongoUserRepository."""
from uuid import uuid4

import pytest

from domain.entities import User
from domain.enums import UserRole
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.mongo.repositories.mongo_user_repository import MongoUserRepository


@pytest.fixture
def repo(mongo_db):
    return MongoUserRepository(mongo_db)


def test_save_and_get_user(repo):
    user = User(id=uuid4(), username="gandalf")
    repo.save(user)

    result = repo.get(user.id)

    assert result.id == user.id
    assert result.username == "gandalf"
    assert result.role == UserRole.AUTHENTICATED


def test_get_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.get(uuid4())


def test_save_updates_existing_user(repo):
    user = User(id=uuid4(), username="gandalf")
    repo.save(user)

    user.username = "gandalf_the_white"
    repo.save(user)

    result = repo.get(user.id)
    assert result.username == "gandalf_the_white"


def test_save_updates_user_role(repo):
    user = User(id=uuid4(), username="gandalf")
    repo.save(user)

    user.role = UserRole.MASTER
    repo.save(user)

    result = repo.get(user.id)
    assert result.role == UserRole.MASTER


def test_delete_user(repo):
    user = User(id=uuid4(), username="saruman")
    repo.save(user)
    repo.delete(user.id)

    with pytest.raises(EntityNotFoundError):
        repo.get(user.id)


def test_delete_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.delete(uuid4())


def test_exists_returns_true(repo):
    user = User(id=uuid4(), username="radagast")
    repo.save(user)

    assert repo.exists(user.id) is True


def test_exists_returns_false(repo):
    assert repo.exists(uuid4()) is False


def test_get_by_username(repo):
    user = User(id=uuid4(), username="frodo")
    repo.save(user)

    result = repo.get_by_username("frodo")
    assert result is not None
    assert result.id == user.id


def test_get_by_username_returns_none_when_not_found(repo):
    assert repo.get_by_username("nobody") is None


def test_list_all(repo):
    users = [User(id=uuid4(), username=f"user_{i}") for i in range(3)]
    for u in users:
        repo.save(u)

    result = repo.list_all()
    assert len(result) == 3
