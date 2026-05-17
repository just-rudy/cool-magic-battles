import random
from uuid import UUID, uuid4

from application.interfaces.game_repository import GameRepository
from application.interfaces.user_repository import UserRepository
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_state_manager import GameStateManager
from domain.entities import Card, Deck, Game, Player
from domain.enums import GameStatus


class GameLogic:
    def __init__(
        self,
        game_repository: GameRepository,
        user_repository: UserRepository,
        card_logic: CardLogic,
        deck_service: DeckService,
        game_state_manager: GameStateManager,
    ) -> None:
        self._repo = game_repository
        self._us_repo = user_repository
        self._card_logic = card_logic
        self._deck_service = deck_service
        self._state = game_state_manager

    def _get_player(self, game: Game, player_id: UUID) -> Player:
        for player in game.players:
            if player.id == player_id:
                return player
        raise ValueError("Player not found in game")

    def _get_card(self, deck: Deck, card_id: UUID) -> Card:
        for card in deck.cards:
            if card.id == card_id:
                return card
        raise ValueError("Card not in deck")

    def _player_cards(self, player: Player) -> list[Card]:
        return [
            *player.draw_deck.cards,
            *player.hand_deck.cards,
            *player.table_deck.cards,
            *player.discard_deck.cards,
        ]

    def _determine_winner(self, game: Game) -> Player:
        if not game.players:
            raise ValueError("No players in the game")

        def ranking(player: Player) -> tuple[int, int, int, str, str]:
            cards = self._player_cards(player)
            cool_points = sum(card.cool_points for card in cards)
            cards_count = len(cards)
            # Final fallback is deterministic because card type tie-breakers
            # are not modeled in the current simplified domain yet.
            return (
                cool_points,
                cards_count,
                -player.turn_order,
                player.nickname,
                str(player.id),
            )

        return max(game.players, key=ranking)

    def create_game(self, host_user_id: UUID) -> Game:
        game = Game(id=uuid4(), host_user_id=host_user_id)
        self._repo.save(game)
        return game

    def start_game(self, game_id: UUID) -> None:
        game = self._repo.get(game_id)

        if game.status == GameStatus.IN_PROGRESS:
            raise ValueError("Game already in progress")

        game.status = GameStatus.IN_PROGRESS
        game.winner_id = None
        game = self.order_player_turns(game)

        if not game.players:
            raise ValueError("No players in the game")

        game.cur_turn = 0
        game.cur_player_id = game.players[0].id

        self._repo.save(game)

    def order_player_turns(self, game: Game) -> Game:
        random.shuffle(game.players)
        for i, player in enumerate(game.players):
            player.turn_order = i
        return game

    def add_player(self, game_id: UUID, user_id: UUID) -> Player:
        game = self._repo.get(game_id)

        if any(player.user_id == user_id for player in game.players):
            raise ValueError("User is already in the game")

        user = self._us_repo.get(user_id)

        player = Player(id=uuid4(), user_id=user_id, nickname=user.username)

        game.players.append(player)
        self._repo.save(game)
        return player

    def buy_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> None:
        game = self._repo.get(game_id)
        player = self._get_player(game, player_id)

        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game not in progress")

        if not self._state.validate_turn(game, player_id):
            raise ValueError("Another player's turn")

        card = self._get_card(game.market_deck, card_id)

        if not self._card_logic.can_purchase(player, card):
            raise ValueError("Card can't be purchased")

        player.cur_echo -= card.cost
        player.discard_deck.cards.append(card)
        game.market_deck.cards.remove(card)

        self._repo.save(game)

    def play_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> None:
        game = self._repo.get(game_id)
        player = self._get_player(game, player_id)

        if game.status != GameStatus.IN_PROGRESS:
            raise ValueError("Game not in progress")

        if not self._state.validate_turn(game, player_id):
            raise ValueError("Another player's turn")

        card = self._get_card(player.hand_deck, card_id)

        if not self._card_logic.can_be_played(player, card):
            raise ValueError("Card can't be played")

        self._card_logic.apply_effect(player, card)
        player.hand_deck.cards.remove(card)
        player.table_deck.cards.append(card)

        self._repo.save(game)

    def end_turn(self, game_id: UUID, player_id: UUID) -> None:
        game = self._repo.get(game_id)

        if not self._state.validate_turn(game, player_id):
            raise ValueError("Another player's turn")

        player = self._get_player(game, player_id)
        player.cur_echo = player.base_echo
        player.discard_deck.cards.extend(player.hand_deck.cards)
        player.discard_deck.cards.extend(player.table_deck.cards)
        player.hand_deck.cards.clear()
        player.table_deck.cards.clear()

        if len(player.draw_deck.cards) < player.hand_size:
            player.draw_deck.cards.extend(player.discard_deck.cards)
            player.discard_deck.cards.clear()
            self._deck_service.shuffle(player.draw_deck)

        player.hand_deck.cards.extend(
            self._deck_service.draw(player.draw_deck, player.hand_size)
        )

        self._state.next_turn(game)
        self._repo.save(game)

    def finish_game(self, game_id: UUID, player_id: UUID) -> None:
        game = self._repo.get(game_id)
        self._get_player(game, player_id)

        if game.status == GameStatus.FINISHED:
            raise ValueError("Game already finished")

        winner = self._determine_winner(game)
        game.status = GameStatus.FINISHED
        game.cur_player_id = None
        game.winner_id = winner.id
        self._repo.save(game)
