"""Tests for MongoCardTypeRepository."""
from uuid import uuid4

import pytest

from domain.entities import CardType
from domain.enums import CardAction, UsePattern
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.mongo.repositories.mongo_card_type_repository import (
    MongoCardTypeRepository,
)


@pytest.fixture
def repo(mongo_db):
    return MongoCardTypeRepository(mongo_db)


def _make_ct(action=CardAction.ATTACK, pattern=UsePattern.REG, color="red") -> CardType:
    return CardType(id=uuid4(), action=action, usage_pattern=pattern, color=color)


def test_save_and_get(repo):
    ct = _make_ct()
    repo.save(ct)

    result = repo.get(ct.id)
    assert result.id == ct.id
    assert result.action == CardAction.ATTACK
    assert result.usage_pattern == UsePattern.REG


def test_get_raises_when_not_found(repo):
    with pytest.raises(EntityNotFoundError):
        repo.get(uuid4())


def test_save_updates_existing(repo):
    ct = _make_ct(color="blue")
    repo.save(ct)

    ct.color = "green"
    repo.save(ct)

    result = repo.get(ct.id)
    assert result.color == "green"


def test_delete(repo):
    ct = _make_ct()
    repo.save(ct)
    repo.delete(ct.id)

    with pytest.raises(EntityNotFoundError):
        repo.get(ct.id)


def test_list_all_sorted_by_action(repo):
    types = [
        _make_ct(action=CardAction.HEAL),
        _make_ct(action=CardAction.ATTACK),
        _make_ct(action=CardAction.DRAW),
    ]
    for ct in types:
        repo.save(ct)

    result = repo.list_all()
    actions = [ct.action.value for ct in result]
    assert actions == sorted(actions)


def test_find_by_title(repo):
    ct = _make_ct(action=CardAction.DEF)
    repo.save(ct)

    result = repo.find_by_title("defense")
    assert result is not None
    assert result.action == CardAction.DEF


def test_find_by_title_returns_none(repo):
    assert repo.find_by_title("nonexistent") is None


def test_exists(repo):
    ct = _make_ct()
    repo.save(ct)
    assert repo.exists(str(ct.id)) is True
    assert repo.exists(str(uuid4())) is False
