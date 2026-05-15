from domain.entities import Game
from domain.enums import GameStatus
from infrastructure.db.models import GameModel


class GameMapper:
    @staticmethod
    def to_domain(model: GameModel) -> Game:
        return Game(
            id=model.id,
            host_user_id=model.host_user_id,
            status=GameStatus(model.status),
            cur_turn=model.cur_turn,
            cur_player_id=model.cur_player_id,
            winner_id=model.winner_id,
        )

    @staticmethod
    def to_model(entity: Game) -> GameModel:
        return GameModel(
            id=entity.id,
            host_user_id=entity.host_user_id,
            status=entity.status.value,
            cur_turn=entity.cur_turn,
            cur_player_id=entity.cur_player_id,
            winner_id=entity.winner_id,
        )
