import random
from typing import Any
from uuid import UUID

from application.interfaces.card_repository import CardRepository
from application.interfaces.game_repository import GameRepository
from application.services import GameLogic
from application.services.card_factory import generate_cards
from domain.entities import Card, Game, Player


class GameController:
    def __init__(
        self,
        game_logic: GameLogic,
        game_repository: GameRepository,
        card_repository: CardRepository,
        default_market_size: int,
    ) -> None:
        self._game_logic = game_logic
        self._game_repo = game_repository
        self._card_repo = card_repository
        self._default_market_size = default_market_size
        self._runtime_games: dict[UUID, Game] = {}

    def _refresh_runtime_game(self, game_id: UUID) -> Game:
        game = self._game_repo.get(game_id)
        self._runtime_games[game_id] = game
        return game

    def _get_runtime_game(self, game_id: UUID) -> Game:
        game = self._runtime_games.get(game_id)
        if game is not None:
            return game

        game = self._game_repo.get(game_id)
        self._runtime_games[game_id] = game
        return game

    def create_game(self, host_user_id: UUID) -> Game:
        game = self._game_logic.create_game(host_user_id)
        self._runtime_games[game.id] = game
        return game

    def get_game_by_id(self, game_id: UUID) -> Game:
        return self._get_runtime_game(game_id)

    def join_game(self, game_id: UUID, user_id: UUID) -> Player:
        player = self._game_logic.add_player(game_id, user_id)
        self._refresh_runtime_game(game_id)

        return player

    def show_hand(self, game_id: UUID, player_id: UUID) -> list[dict[str, Any]]:
        game = self._get_runtime_game(game_id)

        player = next((p for p in game.players if p.id == player_id), None)
        if player is None:
            raise ValueError("Player not found")

        return [
            {
                "id": str(card.id),
                "title": card.title,
                "image_id": str(card.image_id),
                "image_title": card.image.title if card.image is not None else None,
                "image_file": card.image.file if card.image is not None else None,
                "cost": card.cost,
                "power": card.power,
                "echo": card.echo,
                "cool_points": card.cool_points,
            }
            for card in player.hand_deck.cards
        ]

    def show_market(self, game_id: UUID) -> list[dict[str, Any]]:
        game = self._get_runtime_game(game_id)

        return [
            {
                "id": str(card.id),
                "title": card.title,
                "image_id": str(card.image_id),
                "image_title": card.image.title if card.image is not None else None,
                "image_file": card.image.file if card.image is not None else None,
                "cost": card.cost,
                "power": card.power,
                "echo": card.echo,
                "cool_points": card.cool_points,
            }
            for card in game.market_deck.cards
        ]

    def generate_decks(self, game_id: UUID) -> None:
        game = self._get_runtime_game(game_id)

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

        self._game_repo.save(game)
        self._runtime_games[game_id] = game

    def start_game(self, game_id: UUID) -> str:
        self._game_logic.start_game(game_id)
        self._refresh_runtime_game(game_id)
        return f"Game {game_id} started"

    def show_game_state(self, game_id: UUID) -> dict[str, Any]:
        game = self._game_repo.get(game_id)
        return {
            "id": str(game.id),
            "host_user_id": str(game.host_user_id),
            "status": game.status,
            "cur_turn": game.cur_turn,
            "cur_player_id": str(game.cur_player_id)
            if game.cur_player_id is not None
            else None,
            "players": [
                {
                    "player_id": str(player.id),
                    "nickname": player.nickname,
                    "health": player.health,
                    "echo": player.cur_echo,
                    "hand_count": len(player.hand_deck.cards),
                    "table_count": len(player.table_deck.cards),
                    "discard_count": len(player.discard_deck.cards),
                    "draw_count": len(player.draw_deck.cards),
                }
                for player in game.players
            ],
        }

    def play_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> str:
        self._game_logic.play_card(game_id, player_id, card_id)
        self._refresh_runtime_game(game_id)
        return f"Card {card_id} was played"

    def buy_card(self, game_id: UUID, player_id: UUID, card_id: UUID) -> str:
        self._game_logic.buy_card(game_id, player_id, card_id)
        self._refresh_runtime_game(game_id)
        return f"Card {card_id} was bought"

    def end_turn(self, game_id: UUID, player_id: UUID) -> str:
        self._game_logic.end_turn(game_id, player_id)
        game = self._refresh_runtime_game(game_id)
        self._refill_market(game)
        self._game_repo.save(game)
        self._runtime_games[game_id] = game
        return f"Player {player_id}'s turn has ended"

    def list_players(self, game_id: UUID) -> list[dict[str, Any]]:
        game = self._game_repo.get(game_id)

        return [
            {
                "player_id": str(p.id),
                "user_id": str(p.user_id),
                "nickname": p.nickname,
                "turn": p.turn_order,
                "hp": p.health,
                "base_echo": p.base_echo,
                "echo": p.cur_echo,
                "hand": len(p.hand_deck.cards),
            }
            for p in game.players
        ]

    def _generate_cards(self, count: int) -> list[Card]:
        return generate_cards(count)

    def _refill_market(self, game: Game) -> None:
        missing_cards_count = self._default_market_size - len(game.market_deck.cards)
        if missing_cards_count <= 0:
            return

        cards = game.game_deck.cards[:missing_cards_count]
        game.market_deck.cards.extend(cards)
        del game.game_deck.cards[: len(cards)]
