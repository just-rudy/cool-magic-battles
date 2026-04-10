from domain.entities.game import Game
from domain.enums import GameStatus
from infrastructure.db.models.game_model import GameModel


class GameMapper:
    @staticmethod
    def to_domain(model: GameModel) -> Game:
        return Game(
            id=model.id,
            host_user_id=model.host_user_id,
            status=GameStatus(model.status),
            current_turn=model.current_turn,
            current_player_id=model.current_player_id,
        )

    @staticmethod
    def to_model(entity: Game) -> GameModel:
        return GameModel(
            id=entity.id,
            host_user_id=entity.host_user_id,
            status=entity.status.value,
            current_turn=entity.current_turn,
            current_player_id=entity.current_player_id,
        )
