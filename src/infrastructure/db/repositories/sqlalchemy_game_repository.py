from uuid import UUID

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from application.interfaces.game_repository import GameRepository
from domain.entities.game import Game
from infrastructure.db.exceptions import EntityNotFoundError, PersistenceError
from infrastructure.db.mappers.game_mapper import GameMapper
from infrastructure.db.mappers.player_mapper import PlayerMapper
from infrastructure.db.models.game_model import GameModel
from infrastructure.db.models.player_model import PlayerModel


class SqlAlchemyGameRepository(GameRepository):
    # Decks and cards inside decks are intentionally left for later iterations

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, game: Game) -> None:
        try:
            model = self._session.get(GameModel, game.id)
            if model is None:
                model = GameMapper.to_model(game)
                self._session.add(model)
                self._session.flush()
            else:
                model.host_user_id = game.host_user_id
                model.status = game.status.value
                model.current_turn = game.current_turn
                model.current_player_id = game.current_player_id

            existing_players = {
                player_model.id: player_model
                for player_model in self._session.query(PlayerModel)
                .filter(PlayerModel.game_id == game.id)
                .all()
            }
            players_ids = set()

            for player in game.players:
                players_ids.add(player.id)
                player_model = existing_players.get(player.id)
                if player_model is None:
                    player_model = PlayerModel(
                        id=player.id,
                        game_id=game.id,
                        user_id=player.user_id,
                        nickname=player.nickname,
                        turn_order=player.turn_order,
                        health=player.health,
                        base_echo=player.base_echo,
                        cur_echo=player.cur_echo,
                        hand_size=player.hand_size,
                    )
                    self._session.add(player_model)
                else:
                    PlayerMapper.update_model(player_model, player)

            for player_id, player_model in existing_players.items():
                if player_id not in players_ids:
                    self._session.delete(player_model)

            self._session.commit()

        except IntegrityError as exc:
            self._session.rollback()
            raise PersistenceError(
                "err: failed to save game - integrity constraint violated"
            ) from exc

        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("err: failed to save game") from exc

    def get(self, game_id: UUID) -> Game:
        model = self._session.get(GameModel, game_id)
        if model is None:
            raise EntityNotFoundError(f"Game {game_id} not found")

        game = GameMapper.to_domain(model)
        player_models = (
            self._session.query(PlayerModel)
            .filter(PlayerModel.game_id == game.id)
            .order_by(PlayerModel.turn_order.asc())
            .all()
        )
        game.players = [
            PlayerMapper.to_domain(player_model) for player_model in player_models
        ]
        return game

    def delete(self, game_id: UUID) -> None:
        model = self._session.get(GameModel, game_id)
        if model is None:
            raise EntityNotFoundError(f"err: game {game_id} not found")

        try:
            self._session.query(PlayerModel).filter(
                PlayerModel.game_id == game_id
            ).delete()
            self._session.delete(model)
            self._session.commit()
        except SQLAlchemyError as exc:
            self._session.rollback()
            raise PersistenceError("err: failed to delete game") from exc

    def exists(self, game_id: UUID) -> bool:
        return self._session.get(GameModel, game_id) is not None
