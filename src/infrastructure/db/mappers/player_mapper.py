from domain.entities import Player
from infrastructure.db.models import PlayerModel


class PlayerMapper:
    @staticmethod
    def to_domain(model: PlayerModel) -> Player:
        return Player(
            id=model.id,
            user_id=model.user_id,
            nickname=model.nickname,
            turn_order=model.turn_order,
            health=model.health,
            base_echo=model.base_echo,
            cur_echo=model.cur_echo,
            hand_size=model.hand_size,
        )

    @staticmethod
    def update_model(model: PlayerModel, entity: Player) -> None:
        model.user_id = entity.user_id
        model.nickname = entity.nickname
        model.turn_order = entity.turn_order
        model.health = entity.health
        model.base_echo = entity.base_echo
        model.cur_echo = entity.cur_echo
        model.hand_size = entity.hand_size
