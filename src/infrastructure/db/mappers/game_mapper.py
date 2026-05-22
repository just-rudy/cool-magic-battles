from domain.entities import Game, PendingAttack
from domain.enums import GameStatus
from infrastructure.db.models import GameModel


class GameMapper:
    @staticmethod
    def to_domain(model: GameModel) -> Game:
        pending_attack = None
        if (
            model.pending_attacker_id is not None
            and model.pending_defender_id is not None
            and model.pending_damage is not None
        ):
            pending_attack = PendingAttack(
                attacker_id=model.pending_attacker_id,
                defender_id=model.pending_defender_id,
                damage=model.pending_damage,
            )

        return Game(
            id=model.id,
            host_user_id=model.host_user_id,
            status=GameStatus(model.status),
            cur_turn=model.cur_turn,
            cur_player_id=model.cur_player_id,
            winner_id=model.winner_id,
            pending_attack=pending_attack,
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
            pending_attacker_id=(
                entity.pending_attack.attacker_id
                if entity.pending_attack is not None
                else None
            ),
            pending_defender_id=(
                entity.pending_attack.defender_id
                if entity.pending_attack is not None
                else None
            ),
            pending_damage=(
                entity.pending_attack.damage
                if entity.pending_attack is not None
                else None
            ),
        )
