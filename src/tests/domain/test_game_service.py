from unittest.mock import Mock
from uuid import uuid4

from application.interfaces.game_repository import GameRepository
from application.interfaces.user_repository import UserRepository
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_service import GameAppService
from application.services.game_state_manager import GameStateManager
from domain.enums import GameStatus


def make_service(
    game_repository: Mock,
    user_repository: Mock,
    card_logic: Mock,
    deck_service: Mock,
    game_state_manager: Mock,
    card_repository: Mock | None = None,
    default_market_size: int = 5,
) -> GameAppService:
    if card_repository is None:
        card_repository = Mock()
        card_repository.list_all.return_value = []
    return GameAppService(
        game_repository=game_repository,
        user_repository=user_repository,
        card_logic=card_logic,
        deck_service=deck_service,
        game_state_manager=game_state_manager,
        card_repository=card_repository,
        default_market_size=default_market_size,
    )


def test_end_turn_refills_market_to_configured_size(
    make_game,
    make_player,
    make_deck,
    make_card,
) -> None:
    game_repository = Mock(spec=GameRepository)
    user_repository = Mock(spec=UserRepository)
    card_logic = Mock(spec=CardLogic)
    deck_service = Mock(spec=DeckService)
    game_state_manager = Mock(spec=GameStateManager)
    game_state_manager.validate_turn.return_value = True
    deck_service.draw.return_value = []

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
    service = make_service(
        game_repository=game_repository,
        user_repository=user_repository,
        card_logic=card_logic,
        deck_service=deck_service,
        game_state_manager=game_state_manager,
        default_market_size=3,
    )

    result = service.end_turn(game.id, player.id)

    assert result is game
    assert game.market_deck.cards == [market_card, *refill_cards]
    assert game.game_deck.cards == []
    assert game_repository.save.call_count == 2
    game_repository.save.assert_called_with(game)
