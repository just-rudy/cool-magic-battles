from typing import Callable
from unittest.mock import Mock
from uuid import uuid4

import pytest
from pytest import MonkeyPatch

from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_logic import GameLogic
from application.services.game_state_manager import GameStateManager
from domain.entities.card import Card
from domain.entities.deck import Deck
from domain.entities.game import Game
from domain.entities.player import Player
from domain.entities.user import User
from domain.enums import GameStatus


@pytest.fixture
def game_logic() -> tuple[GameLogic, Mock, Mock, Mock, Mock, Mock]:
    game_repository = Mock()
    user_repository = Mock()
    card_logic = Mock(spec=CardLogic)
    deck_service = Mock(spec=DeckService)
    state_manager = Mock(spec=GameStateManager)

    logic = GameLogic(
        game_repository=game_repository,
        user_repository=user_repository,
        card_logic=card_logic,
        deck_service=deck_service,
        game_state_manager=state_manager,
    )

    return (
        logic,
        game_repository,
        user_repository,
        card_logic,
        deck_service,
        state_manager,
    )


def test_get_player_returns_player_from_game(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    logic, *_ = game_logic
    player = make_player()
    other_player = make_player()
    game = make_game(host_id=uuid4(), players=[player, other_player])

    result = logic._get_player(game, player.id)

    assert result == player


def test_get_player_raises_error_when_player_not_found_game_empty(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
) -> None:
    logic, *_ = game_logic
    game = make_game(host_id=uuid4(), players=[])

    with pytest.raises(ValueError, match="Player not found in game"):
        logic._get_player(game, uuid4())


def test_get_player_raises_error_when_player_not_found(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    logic, *_ = game_logic
    player = make_player()
    other_player = make_player()
    game = make_game(host_id=uuid4(), players=[other_player])

    with pytest.raises(ValueError, match="Player not found in game"):
        logic._get_player(game, player_id=player.id)


def test_get_card_returns_card_from_deck(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    logic, *_ = game_logic
    card = make_card()
    deck = make_deck(cards=[card])

    result = logic._get_card(deck, card.id)

    assert result == card


def test_get_card_raises_error_when_card_not_found_empty_deck(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_deck: Callable[..., Deck],
) -> None:
    logic, *_ = game_logic
    deck = make_deck(cards=[])

    with pytest.raises(ValueError, match="Card not in deck"):
        logic._get_card(deck, uuid4())


def test_get_card_raises_error_when_card_not_found(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_deck: Callable[..., Deck],
    make_card: Callable[..., Card],
) -> None:
    logic, *_ = game_logic
    card = make_card()
    other_card = make_card()
    deck = make_deck(cards=[other_card])

    with pytest.raises(ValueError, match="Card not in deck"):
        logic._get_card(deck, card.id)


def test_create_game_creates_and_saves_game(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
) -> None:
    logic, game_repository, *_ = game_logic
    host_id = uuid4()

    game = logic.create_game(host_id)

    assert game.host_id == host_id
    game_repository.save.assert_called_once_with(game)


def test_order_player_turns_sets_turn_order_in_shuffled_order(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    monkeypatch: MonkeyPatch,
) -> None:
    logic, *_ = game_logic
    p1 = make_player(nickname="zeta")
    p2 = make_player(nickname="alpha")
    p3 = make_player(nickname="gamma")
    game = make_game(host_id=uuid4(), players=[p1, p2, p3])

    def fake_shuffle(players: list[Player]) -> None:
        players[:] = [p2, p3, p1]

    monkeypatch.setattr("application.services.game_logic.random.shuffle", fake_shuffle)

    result = logic.order_player_turns(game)

    assert result.players == [p2, p3, p1]
    assert result.players[0].turn_order == 0
    assert result.players[1].turn_order == 1
    assert result.players[2].turn_order == 2


def test_start_game_sets_in_progress_orders_players_and_saves(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    monkeypatch: MonkeyPatch,
) -> None:
    logic, game_repository, *_ = game_logic

    p1 = make_player(nickname="b")
    p2 = make_player(nickname="a")
    game = make_game(host_id=uuid4(), players=[p1, p2], status=GameStatus.CREATED)
    game_repository.get.return_value = game

    called = {"value": False}

    def fake_order_player_turns(arg_game: Game) -> Game:
        called["value"] = True
        assert arg_game is game

        arg_game.players[:] = [p2, p1]
        arg_game.players[0].turn_order = 0
        arg_game.players[1].turn_order = 1
        return arg_game

    monkeypatch.setattr(logic, "order_player_turns", fake_order_player_turns)

    logic.start_game(game.id)

    assert game.status == GameStatus.IN_PROGRESS
    assert called["value"] is True
    assert game.players == [p2, p1]
    assert [p.turn_order for p in game.players] == [0, 1]
    game_repository.save.assert_called_once_with(game)


def test_start_game_raises_error_if_already_in_progress(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
) -> None:
    logic, game_repository, *_ = game_logic
    game = make_game(host_id=uuid4(), status=GameStatus.IN_PROGRESS)
    game_repository.get.return_value = game

    with pytest.raises(ValueError, match="Game already in progress"):
        logic.start_game(game.id)


def test_add_player_creates_player_and_saves_game(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_user: Callable[..., User],
) -> None:
    logic, game_repository, user_repository, *_ = game_logic
    user_id = uuid4()
    user = make_user(username="new_user")
    user.id = user_id
    game = make_game(host_id=uuid4(), players=[])

    game_repository.get.return_value = game
    user_repository.get.return_value = user

    player = logic.add_player(game.id, user_id)

    assert player.user_id == user_id
    assert player.nickname == "new_user"
    assert player in game.players
    game_repository.save.assert_called_once_with(game)


def test_add_player_raises_error_if_user_already_in_game(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    logic, game_repository, *_ = game_logic
    user_id = uuid4()
    existing_player = make_player(user_id=user_id)
    game = make_game(host_id=uuid4(), players=[existing_player])
    game_repository.get.return_value = game

    with pytest.raises(ValueError, match="User is already in the game"):
        logic.add_player(game.id, user_id)


def test_buy_card_raises_error_when_game_not_in_progress(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, *_ = game_logic
    player = make_player()
    card = make_card()
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.CREATED,
        current_player_id=player.id,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game

    with pytest.raises(ValueError, match="Game not in progress"):
        logic.buy_card(game.id, player.id, card.id)


def test_buy_card_raises_error_when_not_players_turn(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, _, _, state_manager = game_logic
    player = make_player()
    card = make_card()
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game
    state_manager.validate_turn.side_effect = ValueError("Not your turn")

    with pytest.raises(ValueError, match="Not your turn"):
        logic.buy_card(game.id, player.id, card.id)


def test_buy_card_raises_error_when_card_cant_be_bought(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, card_logic, _, state_manager = game_logic
    player = make_player()
    card = make_card(cost=3)
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        current_player_id=player.id,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    card_logic.can_purchase.return_value = False

    with pytest.raises(ValueError, match="Card can't be purchased"):
        logic.buy_card(game.id, player.id, card.id)


def test_buy_card_moves_card_from_market_to_discard_and_decreases_echo(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, card_logic, _, state_manager = game_logic
    player = make_player(cur_echo=5)
    card = make_card(cost=3)
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        current_player_id=player.id,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    card_logic.can_be_played.return_value = True

    logic.buy_card(game.id, player.id, card.id)

    assert player.cur_echo == 2
    assert card in player.discard_deck.cards
    assert card not in game.market_deck.cards
    game_repository.save.assert_called_once_with(game)


def test_play_card_raises_error_when_game_not_in_progress(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, *_ = game_logic
    player = make_player()
    card = make_card()
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.CREATED,
        current_player_id=player.id,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game

    with pytest.raises(ValueError, match="Game not in progress"):
        logic.play_card(game.id, player.id, card.id)


def test_play_card_raises_error_when_not_players_turn(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, _, _, state_manager = game_logic
    player = make_player()
    card = make_card()
    market_deck = make_deck(cards=[card])
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        market_deck=market_deck,
    )
    game_repository.get.return_value = game
    state_manager.validate_turn.side_effect = ValueError("Not your turn")

    with pytest.raises(ValueError, match="Not your turn"):
        logic.play_card(game.id, player.id, card.id)


def test_play_card_raises_error_when_card_cant_be_played(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, card_logic, _, state_manager = game_logic
    card = make_card()
    hand_deck = make_deck(cards=[card])
    player = make_player(hand_deck=hand_deck)
    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        current_player_id=player.id,
    )

    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    card_logic.can_be_played.return_value = False

    with pytest.raises(ValueError, match="Card can't be played"):
        logic.play_card(game.id, player.id, card.id)


def test_play_card_moves_card_from_hand_to_table_current_expected_domain_behavior(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
) -> None:
    logic, game_repository, _, card_logic, _, state_manager = game_logic
    player = make_player()
    card = make_card()
    player.hand_deck.cards.append(card)

    game = make_game(
        host_id=uuid4(),
        players=[player],
        status=GameStatus.IN_PROGRESS,
        current_player_id=player.id,
    )
    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    card_logic.can_be_played.return_value = True

    logic.play_card(game.id, player.id, card.id)

    assert card not in player.hand_deck.cards
    assert card in player.table_deck.cards
    game_repository.save.assert_called_once_with(game)


def test_end_turn_raises_error_when_not_players_turn(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    logic, game_repository, _, _, _, state_manager = game_logic
    player = make_player()
    game = make_game(host_id=uuid4(), players=[player])
    game_repository.get.return_value = game
    state_manager.validate_turn.side_effect = ValueError("Not your turn")

    with pytest.raises(ValueError, match="Not your turn"):
        logic.end_turn(game.id, player.id)


def test_end_turn_discards_cards_draws_new_hand_calls_next_turn_and_saves(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
) -> None:
    logic, game_repository, _, _, deck_service, state_manager = game_logic

    hand_cards = [make_card(title="h1"), make_card(title="h2")]
    table_cards = [make_card(title="t1")]
    draw_cards = [make_card(title="d1"), make_card(title="d2"), make_card(title="d3")]

    player = make_player(cur_echo=5, hand_size=3)
    player.hand_deck.cards = hand_cards.copy()
    player.table_deck.cards = table_cards.copy()
    player.draw_deck.cards = draw_cards.copy()
    player.discard_deck.cards = []

    game = make_game(host_id=uuid4(), players=[player], current_player_id=player.id)
    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    deck_service.draw.return_value = draw_cards.copy()

    logic.end_turn(game.id, player.id)

    assert player.cur_echo == 0
    assert player.hand_deck.cards == draw_cards
    assert player.table_deck.cards == []
    assert player.discard_deck.cards == hand_cards + table_cards

    deck_service.draw.assert_called_once_with(player.draw_deck, player.hand_size)
    state_manager.next_turn.assert_called_once_with(game)
    game_repository.save.assert_called_once_with(game)


def test_end_turn_shuffles_discard_into_draw_deck_when_cards_are_insufficient(
    game_logic: tuple[GameLogic, Mock, Mock, Mock, Mock, Mock],
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
    make_card: Callable[..., Card],
) -> None:
    logic, game_repository, _, _, deck_service, state_manager = game_logic

    draw_cards = [make_card(title="d1")]
    discard_existing = [make_card(title="old_discard")]
    hand_cards = [make_card(title="h1")]
    table_cards = [make_card(title="t1")]
    new_hand = [make_card(title="n1"), make_card(title="n2")]

    player = make_player(cur_echo=2, hand_size=2)
    player.draw_deck.cards = draw_cards.copy()
    player.discard_deck.cards = discard_existing.copy()
    player.hand_deck.cards = hand_cards.copy()
    player.table_deck.cards = table_cards.copy()

    game = make_game(host_id=uuid4(), players=[player], current_player_id=player.id)
    game_repository.get.return_value = game
    state_manager.validate_turn.return_value = True
    deck_service.draw.return_value = new_hand.copy()

    logic.end_turn(game.id, player.id)

    assert player.cur_echo == 0
    assert (
        player.draw_deck.cards
        == draw_cards + discard_existing + hand_cards + table_cards
    )
    assert player.discard_deck.cards == []
    assert player.table_deck.cards == []
    assert player.hand_deck.cards == new_hand

    deck_service.shuffle.assert_called_once_with(player.draw_deck)
    deck_service.draw.assert_called_once_with(player.draw_deck, player.hand_size)
    state_manager.next_turn.assert_called_once_with(game)
    game_repository.save.assert_called_once_with(game)
