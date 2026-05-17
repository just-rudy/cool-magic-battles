from __future__ import annotations

from collections.abc import Sequence
from typing import Any, cast
from uuid import UUID

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from domain.entities import Player, User
from infrastructure.ui.console.id_utils import short_id


def format_message(message: str) -> Panel:
    return Panel(
        Text.from_markup(f"[bold green]>[/bold green] {escape(message)}"),
        expand=False,
    )


def format_error(message: str) -> Panel:
    return Panel(f"[bold red]!> err:[/bold red] {message}", expand=False)


def format_warn(data: str = "") -> Panel:
    data = (data.strip() + " ") if data else ""
    return Panel(f"[yellow]?> invalid {data}[/yellow]", expand=False)


def _fmt_id(value: Any, *, full: bool) -> str:
    if value is None:
        return ""
    return str(value) if full else short_id(value)


# ======================
# USER
# ======================


def format_user(user: User | None, title: str = "") -> Table | Panel:
    if user is None:
        return format_warn("user")

    table = Table(title=title or "User")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("ID", _fmt_id(user.id, full=True))
    table.add_row("Username", user.username)

    return table


def format_users(users: Sequence[dict[str, Any] | User]) -> Table | Panel:
    if not users:
        return format_warn("users")

    table = Table(title="Users")
    table.add_column("#", justify="right")
    table.add_column("id", style="dim")
    table.add_column("username", style="cyan")

    for i, user in enumerate(users, start=1):
        if isinstance(user, User):
            uid = user.id
            username = user.username
        else:
            uid = cast(UUID, user.get("id"))
            username = cast(str, user.get("username"))

        table.add_row(str(i), _fmt_id(uid, full=True), str(username))

    return table


# ======================
# PLAYER
# ======================


def format_player(
    pl: Player | dict[str, Any] | list[Player | dict[str, Any]],
    title: str = "",
) -> Table | Panel:
    if not pl:
        return format_warn("players")

    players = pl if isinstance(pl, list) else [pl]
    # is_single = not isinstance(pl, list)

    table = Table(title=title or "Players")
    table.add_column("#", justify="right")
    table.add_column("ID", style="dim")
    table.add_column("Nick", style="dark_green")
    table.add_column("Turn")
    table.add_column("Health", style="hot_pink")
    table.add_column("Base echo", style="orange1")
    table.add_column("Cur echo", style="orange1")
    table.add_column("Hand size")

    for i, player in enumerate(players, start=1):
        pid = player.get("id") if isinstance(player, dict) else player.id
        if isinstance(player, dict) and pid is None:
            pid = player.get("player_id")

        nickname = (
            player.get("nickname") if isinstance(player, dict) else player.nickname
        )

        turn_order = (
            player.get("turn_order") if isinstance(player, dict) else player.turn_order
        )
        if isinstance(player, dict) and turn_order is None:
            turn_order = player.get("turn")

        health = player.get("health") if isinstance(player, dict) else player.health
        if isinstance(player, dict) and health is None:
            health = player.get("hp")

        base_echo = (
            player.get("base_echo") if isinstance(player, dict) else player.base_echo
        )

        cur_echo = (
            player.get("cur_echo") if isinstance(player, dict) else player.cur_echo
        )
        if isinstance(player, dict) and cur_echo is None:
            cur_echo = player.get("echo")

        hand_size = (
            player.get("hand_size") if isinstance(player, dict) else player.hand_size
        )
        if isinstance(player, dict) and hand_size is None:
            hand_size = player.get("hand")

        table.add_row(
            str(i),
            _fmt_id(pid, full=True),
            str(nickname),
            str(turn_order),
            str(health),
            str(base_echo),
            str(cur_echo),
            str(hand_size),
        )

    return table


# ======================
# CARDS
# ======================


def format_cards(cards: list[dict[str, Any]]) -> Table | Panel:
    if not cards:
        return format_warn("cards")

    table = Table(title="Cards")
    table.add_column("#", justify="right")
    table.add_column("ID", style="dim")
    table.add_column("Title", style="cyan")
    table.add_column("Cost", justify="right")
    table.add_column("Power", justify="right")
    table.add_column("Echo", justify="right")
    table.add_column("CP", justify="right")

    for i, card in enumerate(cards, start=1):
        table.add_row(
            str(i),
            _fmt_id(card.get("id"), full=True),
            str(card.get("title")),
            str(card.get("cost")),
            str(card.get("power")),
            str(card.get("echo")),
            str(card.get("cool_points", card.get("cool points"))),
        )

    return table


# ======================
# GAME STATE
# ======================


def format_game_state(game: dict[str, Any]) -> Table | Panel:
    if not game:
        return format_warn("game")

    table = Table(title="Game state")
    table.add_column("Field", style="cyan")
    table.add_column("Value")

    table.add_row("Game ID", _fmt_id(game.get("id"), full=True))
    table.add_row("Status", str(game.get("status")))
    table.add_row("Turn", str(game.get("cur_turn")))
    table.add_row(
        "Current player",
        _fmt_id(game.get("cur_player_id"), full=True),
    )

    return table
