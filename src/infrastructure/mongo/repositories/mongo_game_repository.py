"""MongoDB implementation of GameRepository.

Стратегия хранения: вся игра — один документ в коллекции `games`.
Колоды и карты хранятся как вложенные документы (embedded).
Это позволяет атомарно сохранять и загружать состояние игры.

Структура документа:
{
  "_id": "<game_id>",
  "host_user_id": "...",
  "status": "in_progress",
  "cur_turn": 3,
  "cur_player_id": "...",
  "winner_id": null,
  "pending_attack": {"attacker_id": "...", "defender_id": "...", "damage": 5} | null,
  "market_deck": { "id": "...", "type": "market", "if_open": true, "cards": [...] },
  "game_deck":   { "id": "...", "type": "deck",   "if_open": false, "cards": [...] },
  "banish_deck": { "id": "...", "type": "banish", "if_open": false, "cards": [...] },
  "players": [
    {
      "id": "...", "user_id": "...", "nickname": "...",
      "turn_order": 0, "health": 20, "base_echo": 0, "cur_echo": 0,
      "hand_size": 5,
      "draw_deck": { "id": "...", "type": "draw", "if_open": false,
                     "cards": [...] },
      "hand_deck": { "id": "...", "type": "hand", "if_open": true,
                     "cards": [...] },
      "table_deck": { "id": "...", "type": "table", "if_open": true,
                      "cards": [...] },
      "discard_deck": { "id": "...", "type": "discard", "if_open": true,
                        "cards": [...] }
    }
  ]
}
"""
from uuid import UUID

from pymongo.database import Database
from pymongo.errors import PyMongoError

from application.interfaces.game_repository import GameRepository
from domain.entities import Game
from infrastructure.db.exceptions import EntityNotFoundError, PersistenceError
from infrastructure.mongo.mappers.game_mapper import MongoGameMapper


class MongoGameRepository(GameRepository):
    COLLECTION = "games"

    def __init__(self, db: Database) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]

    def save(self, game: Game) -> None:
        doc = MongoGameMapper.to_document(game)
        try:
            self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        except PyMongoError as exc:
            raise PersistenceError("failed to save game") from exc

    def get(self, game_id: UUID) -> Game:
        doc = self._col.find_one({"_id": str(game_id)})
        if doc is None:
            raise EntityNotFoundError(f"Game {game_id} not found")
        return MongoGameMapper.to_entity(doc)

    def delete(self, game_id: UUID) -> None:
        result = self._col.delete_one({"_id": str(game_id)})
        if result.deleted_count == 0:
            raise EntityNotFoundError(f"game {game_id} not found")

    def exists(self, game_id: UUID) -> bool:
        return self._col.count_documents({"_id": str(game_id)}, limit=1) > 0

    def list_all(self) -> list["Game"]:
        docs = self._col.find({}, {
            "_id": 1, "host_user_id": 1, "name": 1,
            "status": 1, "cur_turn": 1, "cur_player_id": 1,
            "winner_id": 1, "pending_attack": 1,
            "market_deck": 1, "game_deck": 1, "banish_deck": 1,
            "players": 1,
        })
        return [MongoGameMapper.to_entity(doc) for doc in docs]

    def get_by_name(self, name: str) -> "Game | None":
        doc = self._col.find_one({"name": name})
        if doc is None:
            return None
        return MongoGameMapper.to_entity(doc)
