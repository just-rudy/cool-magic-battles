from uuid import UUID
from domain.entities import Game


class GameStateManager:
    def validate_turn(self, game: Game, player_id: UUID) -> bool:
        if game.cur_player_id != player_id:
            raise ValueError("Not your turn")
        return True

    def next_turn(self, game: Game) -> None:
        if not game.players:
            raise ValueError("No players in the game")

        game.cur_turn += 1
        new_curr = (game.cur_turn) % len(game.players)

        player_found_flag = False

        for player in game.players:
            if player.turn_order == new_curr:
                game.cur_player_id = player.id
                player_found_flag = True
                break

        if not player_found_flag:
            raise ValueError("No next turn player found")
