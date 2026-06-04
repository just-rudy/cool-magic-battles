import re
from uuid import uuid4

import pytest
from sqlalchemy.orm import Session

from application.dto.requests import CreateGameRequest
from application.interfaces.card_repository import CardRepository
from application.interfaces.card_type_repository import CardTypeRepository
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_service import GameAppService
from application.services.game_state_manager import GameStateManager
from domain.entities import User
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)
from infrastructure.db.repositories.sqlalchemy_card_type_repository import (
    SqlAlchemyCardTypeRepository,
)
from infrastructure.db.repositories.sqlalchemy_game_repository import (
    SqlAlchemyGameRepository,
)
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def _service(session: Session) -> GameAppService:
    game_repo = SqlAlchemyGameRepository(session)
    user_repo = SqlAlchemyUserRepository(session)
    card_repo: CardRepository = SqlAlchemyCardRepository(session)
    card_type_repo: CardTypeRepository = SqlAlchemyCardTypeRepository(session)
    return GameAppService(
        game_repository=game_repo,
        user_repository=user_repo,
        card_logic=CardLogic(),
        deck_service=DeckService(),
        game_state_manager=GameStateManager(),
        card_repository=card_repo,
        card_type_repository=card_type_repo,
    )


def test_resolve_game_name_custom_and_default(session: Session) -> None:
    service = _service(session)
    host = User(id=uuid4(), username="host")
    SqlAlchemyUserRepository(session).save(host)

    custom = service.create_new_game(
        CreateGameRequest(host_user_id=host.id, name="battle1")
    )
    assert custom.name == "battle1"

    auto = service.create_new_game(CreateGameRequest(host_user_id=host.id))
    assert re.fullmatch(r"game-\d+", auto.name)


def test_resolve_game_id_by_name(session: Session) -> None:
    service = _service(session)
    host = User(id=uuid4(), username="host")
    SqlAlchemyUserRepository(session).save(host)

    game = service.create_new_game(
        CreateGameRequest(host_user_id=host.id, name="joinme")
    )
    resolved = service.resolve_game_id("joinme")
    assert resolved == game.id


def test_duplicate_game_name_raises(session: Session) -> None:
    service = _service(session)
    host = User(id=uuid4(), username="host")
    SqlAlchemyUserRepository(session).save(host)

    service.create_new_game(CreateGameRequest(host_user_id=host.id, name="taken"))
    with pytest.raises(ValueError, match="already taken"):
        service.create_new_game(CreateGameRequest(host_user_id=host.id, name="taken"))
