from uuid import UUID

# from domain.entities.game import Game
from domain.enums import GameStatus
from infrastructure.db.mappers.game_mapper import GameMapper
from infrastructure.db.models import GameModel

game_model = GameModel(
    id=UUID("11111111-1111-1111-1111-111111111111"),
    host_user_id=UUID("22222222-2222-2222-2222-222222222222"),
    status=GameStatus.CREATED.value,
    cur_turn=0,
    cur_player_id=None,
)

game = GameMapper().to_domain(game_model)
game_model_converted = GameMapper().to_model(game)

# print(game)
print(game.status)
print(game.status.value)
