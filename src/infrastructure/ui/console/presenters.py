from typing import Any


class GameStatePresenter:
    @staticmethod
    def present(state: dict[str, Any]) -> str:
        lines = [
            f"Game: {state['game_id']}",
            f"Game state: {state['status']}",
            f"Turn: {state['cur_turn']}",
            f"Current player: {state['cur_player_id']}",
            "Players:",
        ]
        for player in state["players"]:
            lines.append(
                f"- {player['nickname']} | "
                f"HP={player['health']} | Echo={player['echo']} "
                f"| hand={player['hand_count']} "
                f"| table={player['table_count']} "
                f"| discard={player['discard_count']} | draw={player['draw_count']}"
            )
        return "\n".join(lines)
