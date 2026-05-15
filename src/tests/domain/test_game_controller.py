from collections.abc import Callable
from unittest.mock import Mock
from uuid import uuid4

from application.controllers.game_controller import GameController
from application.interfaces.card_repository import CardRepository
from application.interfaces.game_repository import GameRepository
from application.services import GameLogic
from domain.entities import Card, Deck, Game, Player
from domain.enums import GameStatus


def make_controller(
    game_logic: Mock,
    game_repository: Mock,
    *,
    default_market_size: int,
) -> GameController:
    return GameController(
        game_logic=game_logic,
        game_repository=game_repository,
        card_repository=Mock(spec=CardRepository),
        default_market_size=default_market_size,
    )


def test_generate_decks_uses_configured_market_size(
    make_game: Callable[..., Game],
    make_player: Callable[..., Player],
) -> None:
    game_logic = Mock(spec=GameLogic)
    game_repository = Mock(spec=GameRepository)
    player = make_player(hand_size=3)
    game = make_game(host_user_id=uuid4(), players=[player])
    game_repository.get.return_value = game
    controller = make_controller(
        game_logic,
        game_repository,
        default_market_size=3,
    )

    controller.generate_decks(game.id)

    assert len(game.market_deck.cards) == 3
    assert len(game.game_deck.cards) == 37
    game_repository.save.assert_called_once_with(game)


def test_end_turn_refills_market_to_configured_size(
    make_game: Callable[..., Game],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
    make_player: Callable[..., Player],
) -> None:
    game_logic = Mock(spec=GameLogic)
    game_repository = Mock(spec=GameRepository)
    player = make_player()
    market_card = make_card(title="Market")
    refill_cards = [make_card(title="Refill 1"), make_card(title="Refill 2")]
    game = make_game(
        host_user_id=uuid4(),
        status=GameStatus.IN_PROGRESS,
        players=[player],
        cur_player_id=player.id,
        market_deck=make_deck(cards=[market_card]),
        game_deck=make_deck(cards=refill_cards.copy()),
    )
    game_repository.get.return_value = game
    controller = make_controller(
        game_logic,
        game_repository,
        default_market_size=3,
    )

    result = controller.end_turn(game.id, player.id)

    game_logic.end_turn.assert_called_once_with(game.id, player.id)
    assert result == f"Player {player.id}'s turn has ended"
    assert game.market_deck.cards == [market_card, *refill_cards]
    assert game.game_deck.cards == []
    game_repository.save.assert_called_once_with(game)


def test_end_turn_refills_market_with_available_cards_only(
    make_game: Callable[..., Game],
    make_card: Callable[..., Card],
    make_deck: Callable[..., Deck],
    make_player: Callable[..., Player],
) -> None:
    game_logic = Mock(spec=GameLogic)
    game_repository = Mock(spec=GameRepository)
    player = make_player()
    market_card = make_card(title="Market")
    refill_card = make_card(title="Refill")
    game = make_game(
        host_user_id=uuid4(),
        status=GameStatus.IN_PROGRESS,
        players=[player],
        cur_player_id=player.id,
        market_deck=make_deck(cards=[market_card]),
        game_deck=make_deck(cards=[refill_card]),
    )
    game_repository.get.return_value = game
    controller = make_controller(
        game_logic,
        game_repository,
        default_market_size=3,
    )

    controller.end_turn(game.id, player.id)

    assert game.market_deck.cards == [market_card, refill_card]
    assert game.game_deck.cards == []
    game_repository.save.assert_called_once_with(game)
