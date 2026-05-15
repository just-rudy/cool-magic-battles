from typing import Any, cast
from uuid import UUID

from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from application.controllers.card_controller import CardController
from application.controllers.game_controller import GameController
from application.controllers.user_controller import UserController
from domain.entities import Player
from infrastructure.logging.logger import get_logger
from infrastructure.ui.console.formatters import (
    format_cards,
    format_game_state,
    format_message,
    format_player,
    format_user,
    format_users,
    format_warn,
)
from infrastructure.ui.console.id_utils import is_valid_uuid
from infrastructure.ui.console.menu import print_menu
from infrastructure.ui.console.parser import ParsedInstruction
from infrastructure.ui.console.prompts import (
    read_uuid_optional,
    read_word,
    read_word_optional,
)
from infrastructure.ui.console.state import ConsoleState

logger = get_logger("ui.console.handler")


class ConsoleHandler:
    def __init__(
        self,
        game_ctrl: GameController,
        user_ctrl: UserController,
        card_ctrl: CardController,
    ) -> None:
        self.game = game_ctrl
        self.user = user_ctrl
        self.card = card_ctrl
        self.cnsl = Console()

    def _cancel(self) -> Panel:
        logger.info("Command cancelled by empty input")
        return format_message("command cancelled")

    def _resolve_user_id(self, raw: str | None, state: ConsoleState) -> UUID | None:
        if raw:
            if is_valid_uuid(raw):
                return UUID(raw)

            users = self.user.list_users()
            for user in users:
                if str(user["username"]).lower() == raw.lower():
                    return UUID(str(user["id"]))

            raise ValueError(f"user '{raw}' not found")

        if state.cur_user:
            return state.cur_user.id

        raw_user = read_word_optional("user_id/username: ", self.cnsl)
        if raw_user is None:
            return None

        if is_valid_uuid(raw_user):
            return UUID(raw_user)

        users = self.user.list_users()
        for user in users:
            if str(user["username"]).lower() == raw_user.lower():
                return UUID(str(user["id"]))

        raise ValueError(f"user '{raw_user}' not found")

    def _resolve_game_id(self, raw: str | None, state: ConsoleState) -> UUID | None:
        if raw:
            if is_valid_uuid(raw):
                return UUID(raw)
            raise ValueError("game id must be full uuid")

        if state.cur_game:
            return state.cur_game.id

        return read_uuid_optional("game_id: ", self.cnsl)

    def _resolve_player_id(self, raw: str | None, state: ConsoleState) -> UUID | None:
        if raw:
            if is_valid_uuid(raw):
                return UUID(raw)
            raise ValueError("player id must be full uuid")

        if state.cur_player:
            return state.cur_player.id

        return read_uuid_optional("player_id: ", self.cnsl)

    def _sync_current_player(
        self,
        state: ConsoleState,
        game_id: UUID,
        player_id: UUID | None = None,
    ) -> None:
        game = self.game.get_game_by_id(game_id)
        state.cur_game = game

        target_player_id = player_id
        if target_player_id is None and state.cur_player is not None:
            target_player_id = state.cur_player.id
        if target_player_id is None:
            target_player_id = game.cur_player_id

        state.cur_player = next(
            (player for player in game.players if player.id == target_player_id),
            None,
        )

    def _set_current_user_player(
        self, state: ConsoleState, user_id: UUID, game_id: UUID
    ) -> Player:
        game = self.game.get_game_by_id(game_id)
        player = next((p for p in game.players if p.user_id == user_id), None)
        if player is None:
            raise ValueError("user is not a player in this game")

        state.cur_user = self.user.get_user_by_id(user_id)
        state.cur_game = game
        state.cur_player = player

        return player

    def _resolve_card_from_hand(
        self,
        raw: str | None,
        game_id: UUID,
        player_id: UUID,
    ) -> UUID | None:
        if not raw:
            raw = read_word_optional("card_id/title: ", self.cnsl)
            if raw is None:
                return None

        if is_valid_uuid(raw):
            return UUID(raw)

        cards = self.game.show_hand(game_id, player_id)
        for card in cards:
            if str(card["title"]).lower() == raw.lower():
                return UUID(str(card["id"]))

        raise ValueError(f"card '{raw}' not found in hand")

    def _resolve_card_from_market(
        self,
        raw: str | None,
        game_id: UUID,
    ) -> UUID | None:
        if not raw:
            raw = read_word_optional("card_id/title: ", self.cnsl)
            if raw is None:
                return None

        if is_valid_uuid(raw):
            return UUID(raw)

        cards = self.game.show_market(game_id)
        for card in cards:
            if str(card["title"]).lower() == raw.lower():
                return UUID(str(card["id"]))

        raise ValueError(f"card '{raw}' not found in market")

    def _handle_reg(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling reg command")

        username = cmd.nickname if cmd.nickname else read_word("username: ", self.cnsl)

        user = self.user.register_user(username)
        state.cur_user = user
        state.cur_player = None

        logger.info(f"User {user.username} registered and logged in, id=[{user.id}]")
        return format_message(
            f"user {user.username} id=[{user.id}] was added and logged"
        )

    def _handle_login(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling login command")

        user_id = self._resolve_user_id(cmd.user_id, state)
        if user_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        player = self._set_current_user_player(state, user_id, game_id)

        logger.info(
            f"Current user/player switched, game id=[{game_id}] "
            f"user id=[{user_id}] player id=[{player.id}]"
        )
        return format_message(
            f"logged as {player.nickname}, player id=[{player.id}], game id=[{game_id}]"
        )

    def _handle_ext(self) -> Panel:
        logger.info("Handling exit command")
        return format_message("exitting")

    def _handle_new(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling new command")

        user_id = self._resolve_user_id(cmd.user_id, state)
        logger.info(f"Registering new game, host_user_id=[{user_id}]")

        if not user_id:
            raise ValueError("host user id is required to create a game")
            return self._cancel()

        game = self.game.create_game(user_id)
        player = self.game.join_game(game.id, user_id)

        state.cur_game = game
        state.cur_player = player

        logger.info(
            f"Created new game id=[{game.id}] and joined player id=[{player.id}] "
            f"from user id=[{user_id}]"
        )
        return format_message(
            f"game id=[{game.id}] was created and player id=[{player.id}] "
            f"joined from user id=[{user_id}]"
        )

    def _handle_gen_decks(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling gen_decks command")

        game_id = self._resolve_game_id(cmd.game_id, state)

        if game_id is None:
            return self._cancel()

        self.game.generate_decks(game_id)

        logger.info(f"Decks generated for game id=[{game_id}]")
        return format_message(f"decks generated for game id=[{game_id}]")

    def _handle_run(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling run command")

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        result = self.game.start_game(game_id)
        self._sync_current_player(state, game_id)

        logger.info(f"Game started, game id=[{game_id}]")
        return format_message(result)

    def _handle_join(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling join command")

        user_id = self._resolve_user_id(cmd.user_id, state)
        if user_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        player = self.game.join_game(game_id, user_id)

        state.cur_user = self.user.get_user_by_id(user_id)
        state.cur_game = self.game.get_game_by_id(game_id)
        state.cur_player = player

        logger.info(
            f"Player joined, game id=[{game_id}] user id=[{user_id}] "
            f"player id=[{player.id}]"
        )
        return format_message(
            f"player {player.nickname} id=[{player.id}] joined game id=[{game_id}]"
        )

    def _handle_game(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling game command")

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        state.cur_game = self.game.get_game_by_id(game_id)

        logger.info(f"Showing game state, game id=[{game_id}]")
        return format_game_state(self.game.show_game_state(game_id))

    def _handle_play(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling play command")

        player_id = self._resolve_player_id(None, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        card_id = self._resolve_card_from_hand(cmd.card_ref, game_id, player_id)
        if card_id is None:
            return self._cancel()

        result = self.game.play_card(game_id, player_id, card_id)
        self._sync_current_player(state, game_id, player_id)

        logger.info(
            f"Card played, game id=[{game_id}] player id=[{player_id}] "
            f"card id=[{card_id}]"
        )
        return format_message(result)

    def _handle_buy(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling buy command")

        player_id = self._resolve_player_id(None, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        card_id = self._resolve_card_from_market(cmd.card_ref, game_id)
        if card_id is None:
            return self._cancel()

        result = self.game.buy_card(game_id, player_id, card_id)
        self._sync_current_player(state, game_id, player_id)

        logger.info(
            f"Card bought, game id=[{game_id}] player id=[{player_id}] "
            f"card id=[{card_id}]"
        )
        return format_message(result)

    def _handle_end(self, cmd: ParsedInstruction, state: ConsoleState) -> Panel:
        logger.info("Handling end command")

        player_id = self._resolve_player_id(None, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        result = self.game.end_turn(game_id, player_id)
        self._sync_current_player(state, game_id, player_id)

        logger.info(f"Turn ended, game id=[{game_id}] player id=[{player_id}]")
        return format_message(result)

    def _handle_hand(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling hand command")

        player_id = self._resolve_player_id(cmd.player_id, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(None, state)
        if game_id is None:
            return self._cancel()

        logger.info(f"Showing hand, game id=[{game_id}] player id=[{player_id}]")
        return format_cards(self.game.show_hand(game_id, player_id))

    def _handle_draw(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling draw command")

        player_id = self._resolve_player_id(cmd.player_id, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(None, state)
        if game_id is None:
            return self._cancel()

        game = self.game.get_game_by_id(game_id)
        player = next((p for p in game.players if p.id == player_id), None)
        if player is None:
            raise ValueError("player not found")

        cards = [
            {
                "id": str(card.id),
                "title": card.title,
                "cost": card.cost,
                "power": card.power,
                "echo": card.echo,
                "cool_points": card.cool_points,
            }
            for card in player.draw_deck.cards
        ]

        logger.info(f"Showing draw deck, game id=[{game_id}] player id=[{player_id}]")
        return format_cards(cards)

    def _handle_discard(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling discard command")

        player_id = self._resolve_player_id(cmd.player_id, state)
        if player_id is None:
            return self._cancel()

        game_id = self._resolve_game_id(None, state)
        if game_id is None:
            return self._cancel()

        game = self.game.get_game_by_id(game_id)
        player = next((p for p in game.players if p.id == player_id), None)
        if player is None:
            raise ValueError("player not found")

        cards = [
            {
                "id": str(card.id),
                "title": card.title,
                "cost": card.cost,
                "power": card.power,
                "echo": card.echo,
                "cool_points": card.cool_points,
            }
            for card in player.discard_deck.cards
        ]

        logger.info(
            f"Showing discard deck, game id=[{game_id}] player id=[{player_id}]"
        )
        return format_cards(cards)

    def _handle_market(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling market command")

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        logger.info(f"Showing market, game id=[{game_id}]")
        return format_cards(self.game.show_market(game_id))

    def _handle_players(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Table | Panel:
        logger.info("Handling players command")

        game_id = self._resolve_game_id(cmd.game_id, state)
        if game_id is None:
            return self._cancel()

        logger.info(f"Showing players, game id=[{game_id}]")

        raw_players = self.game.list_players(game_id)
        players: list[dict[str, Any]] = [
            {
                "id": player["player_id"],
                "nickname": player["nickname"],
                "turn_order": player["turn"],
                "health": player["hp"],
                "base_echo": player["base_echo"],
                "cur_echo": player["echo"],
                "hand_size": player["hand"],
            }
            for player in raw_players
        ]

        return format_player(
            cast(list[Player | dict[str, Any]], players), title="Players"
        )

    def _handle_users(self) -> Table | Panel:
        logger.info("Handling users command")
        return format_users(self.user.list_users())

    def _handle_all(self) -> Table | Panel:
        logger.info("Handling all command")
        return format_cards(self.card.list_cards())

    def _handle_cur_u(self, state: ConsoleState) -> Table | Panel:
        logger.info("Handling cur_u command")
        return format_user(state.cur_user, title="Current user")

    def _handle_cur_p(self, state: ConsoleState) -> Table | Panel:
        logger.info("Handling cur_p command")
        if state.cur_game is not None and state.cur_player is not None:
            self._sync_current_player(state, state.cur_game.id, state.cur_player.id)

        if state.cur_player:
            return format_player(state.cur_player, title="Current player")
        return format_warn("no current player")

    def _handle_cur_g(self, state: ConsoleState) -> Table | Panel:
        logger.info("Handling cur_g command")

        if state.cur_game is None:
            return format_warn("no current game")

        return format_game_state(self.game.show_game_state(state.cur_game.id))

    def _handle_menu(self) -> Panel:
        logger.info("Handling menu command")
        return print_menu()

    def dispatch(
        self, cmd: ParsedInstruction, state: ConsoleState
    ) -> Panel | Table | None:
        logger.info(f"Dispatch command: task={cmd.task}")

        if cmd.task == "reg":
            return self._handle_reg(cmd, state)
        if cmd.task in {"login", "as"}:
            return self._handle_login(cmd, state)
        if cmd.task == "ext":
            return self._handle_ext()
        if cmd.task == "new":
            return self._handle_new(cmd, state)
        if cmd.task == "gen_decks":
            return self._handle_gen_decks(cmd, state)
        if cmd.task == "run":
            return self._handle_run(cmd, state)
        if cmd.task == "join":
            return self._handle_join(cmd, state)
        if cmd.task == "game":
            return self._handle_game(cmd, state)
        if cmd.task == "play":
            return self._handle_play(cmd, state)
        if cmd.task == "buy":
            return self._handle_buy(cmd, state)
        if cmd.task == "end":
            return self._handle_end(cmd, state)
        if cmd.task == "hand":
            return self._handle_hand(cmd, state)
        if cmd.task == "draw":
            return self._handle_draw(cmd, state)
        if cmd.task == "discard":
            return self._handle_discard(cmd, state)
        if cmd.task == "market":
            return self._handle_market(cmd, state)
        if cmd.task == "players":
            return self._handle_players(cmd, state)
        if cmd.task == "users":
            return self._handle_users()
        if cmd.task == "all":
            return self._handle_all()
        if cmd.task == "cur_u":
            return self._handle_cur_u(state)
        if cmd.task == "cur_p":
            return self._handle_cur_p(state)
        if cmd.task == "cur_g":
            return self._handle_cur_g(state)
        if cmd.task == "menu":
            return self._handle_menu()

        logger.warning(f"Unknown command received: task={cmd.task}")
        raise ValueError("unknown instruction")
