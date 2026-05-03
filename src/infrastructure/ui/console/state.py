from dataclasses import dataclass

from domain.entities import Game, Player, User


@dataclass
class ConsoleState:
    cur_user: User | None = None
    cur_game: Game | None = None
    cur_player: Player | None = None
