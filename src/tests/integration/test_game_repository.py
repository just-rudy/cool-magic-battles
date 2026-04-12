from uuid import uuid4

from domain.entities.game import Game
from domain.entities.player import Player
from domain.entities.user import User
from domain.enums import GameStatus
from infrastructure.db.repositories.sqlalchemy_game_repository import (
    SqlAlchemyGameRepository,
)
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def test_save_and_get_game_with_players(session: object) -> None:
    user_repo = SqlAlchemyUserRepository(session)
    game_repo = SqlAlchemyGameRepository(session)

    host = User(id=uuid4(), username="host")
    guest = User(id=uuid4(), username="guest")
    user_repo.save(host)
    user_repo.save(guest)

    game = Game(id=uuid4(), host_user_id=host.id, status=GameStatus.CREATED)
    game.players.append(
        Player(id=uuid4(), user_id=host.id, nickname="host", turn_order=0)
    )
    game.players.append(
        Player(id=uuid4(), user_id=guest.id, nickname="guest", turn_order=1)
    )

    game_repo.save(game)
    loaded = game_repo.get(game.id)

    assert loaded.id == game.id
    assert len(loaded.players) == 2
    assert loaded.players[0].nickname == "host"
