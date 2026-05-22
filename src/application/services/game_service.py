import random
from uuid import UUID

from application.dto.requests import CreateGameRequest
from application.interfaces.card_repository import CardRepository
from application.interfaces.game_repository import GameRepository
from application.interfaces.user_repository import UserRepository
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_logic import GameLogic
from application.services.game_state_manager import GameStateManager
from domain.entities import Card, Game


class GameAppService:
    def __init__(
        self,
        game_repository: GameRepository,
        user_repository: UserRepository,
        card_logic: CardLogic,
        deck_service: DeckService,
        game_state_manager: GameStateManager,
        card_repository: CardRepository,
        default_market_size: int = 5,
    ) -> None:
        self._game_repository = game_repository
        self._card_repository = card_repository
        self._default_market_size = default_market_size
        self._logic = GameLogic(
            game_repository=game_repository,
            user_repository=user_repository,
            card_logic=card_logic,
            deck_service=deck_service,
            game_state_manager=game_state_manager,
        )

    def create_new_game(self, request: CreateGameRequest) -> Game:
        return self._logic.create_game(request.host_user_id)

    def get_game(self, game_id: UUID) -> Game:
        return self._game_repository.get(game_id)

    def join_game(self, game_id: UUID, user_id: UUID) -> Game:
        self._logic.add_player(game_id, user_id)
        return self._game_repository.get(game_id)

    def start_game(self, game_id: UUID) -> Game:
        self._generate_decks(game_id)
        self._logic.start_game(game_id)
        return self._game_repository.get(game_id)

    def _generate_decks(self, game_id: UUID) -> None:
        game = self._game_repository.get(game_id)

        if not game.players:
            raise ValueError("No players in game")

        cards = self._generate_cards(50)
        random.shuffle(cards)

        game.market_deck.cards = cards[: self._default_market_size]

        index = self._default_market_size
        for player in game.players:
            player.draw_deck.cards = cards[index : index + 10]
            player.hand_deck.cards = player.draw_deck.cards[: player.hand_size]
            player.draw_deck.cards = player.draw_deck.cards[player.hand_size :]
            player.discard_deck.cards = []
            player.table_deck.cards = []
            index += 10

        game.game_deck.cards = cards[index:]
        self._game_repository.save(game)

    def _refill_market(self, game: Game) -> None:
        missing_cards_count = self._default_market_size - len(game.market_deck.cards)
        if missing_cards_count <= 0:
            return

        cards = game.game_deck.cards[:missing_cards_count]
        game.market_deck.cards.extend(cards)
        del game.game_deck.cards[: len(cards)]

    def _generate_cards(self, count: int) -> list[Card]:
        all_cards = self._card_repository.list_all()
        if len(all_cards) < count:
            raise ValueError(
                f"Not enough cards in the database: need {count}, have {len(all_cards)}. "
                "Run `make db-seed` to populate cards."
            )
        return random.sample(all_cards, count)

    def play_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> Game:
        self._logic.play_card(game_id, player_id, card_id)
        return self._game_repository.get(game_id)

    def buy_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> Game:
        self._logic.buy_card(game_id, player_id, card_id)
        return self._game_repository.get(game_id)

    def end_turn(self, game_id: UUID, player_id: UUID) -> Game:
        self._logic.end_turn(game_id, player_id)
        game = self._game_repository.get(game_id)
        self._refill_market(game)
        self._game_repository.save(game)
        return game

    def finish_game(self, game_id: UUID, player_id: UUID) -> Game:
        self._logic.finish_game(game_id, player_id)
        return self._game_repository.get(game_id)
