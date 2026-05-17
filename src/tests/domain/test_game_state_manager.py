from collections.abc import Callable
from uuid import uuid4

import pytest

from application.services import GameStateManager
from domain.entities import Game, Player


def test_validate_turn_returns_true_for_cur_player(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    manager = GameStateManager()
    player = make_player()
    game = make_game(host_user_id=uuid4(), players=[player], cur_player_id=player.id)

    result = manager.validate_turn(game, player.id)

    assert result is True


def test_validate_turn_raises_error_for_wrong_player(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    manager = GameStateManager()
    player = make_player()
    other_player_id = uuid4()
    game = make_game(
        host_user_id=uuid4(), players=[player], cur_player_id=other_player_id
    )

    with pytest.raises(ValueError, match="Not your turn"):
        manager.validate_turn(game, player.id)


def test_next_turn_switches_to_player_with_next_turn_order(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    manager = GameStateManager()
    p1 = make_player(turn_order=0)
    p2 = make_player(turn_order=1)
    game = make_game(
        host_user_id=uuid4(),
        players=[p1, p2],
        cur_turn=0,
        cur_player_id=p1.id,
    )

    manager.next_turn(game)

    assert game.cur_turn == 1
    assert game.cur_player_id == p2.id


def test_next_turn_wraps_to_first_player(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    manager = GameStateManager()
    p1 = make_player(turn_order=0)
    p2 = make_player(turn_order=1)
    game = make_game(
        host_user_id=uuid4(),
        players=[p1, p2],
        cur_turn=1,
        cur_player_id=p2.id,
    )

    manager.next_turn(game)

    assert game.cur_turn == 2
    assert game.cur_player_id == p1.id


def test_next_turn_raises_error_when_no_players(
    make_game: Callable[..., Game],
) -> None:
    manager = GameStateManager()
    game = make_game(host_user_id=uuid4(), players=[])

    with pytest.raises(ValueError, match="No players in the game"):
        manager.next_turn(game)


def test_next_turn_raises_error_when_next_player_not_found(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    manager = GameStateManager()
    p1 = make_player(turn_order=5)
    p2 = make_player(turn_order=7)
    game = make_game(
        host_user_id=uuid4(),
        players=[p1, p2],
        cur_turn=0,
        cur_player_id=p1.id,
    )

    with pytest.raises(ValueError, match="No next turn player found"):
        manager.next_turn(game)
