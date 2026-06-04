"""MongoDB implementation of CardTypeRepository."""
from uuid import UUID

from pymongo.database import Database
from pymongo.errors import PyMongoError

from application.interfaces.card_type_repository import CardTypeRepository
from domain.entities import CardType
from infrastructure.db.exceptions import EntityNotFoundError, PersistenceError
from infrastructure.mongo.mappers.card_type_mapper import MongoCardTypeMapper


class MongoCardTypeRepository(CardTypeRepository):
    COLLECTION = "card_types"

    def __init__(self, db: Database) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]

    def save(self, card_type: CardType) -> None:
        doc = MongoCardTypeMapper.to_document(card_type)
        try:
            self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        except PyMongoError as exc:
            raise PersistenceError("failed to save card_type") from exc

    def get(self, card_type_id: UUID) -> CardType:
        doc = self._col.find_one({"_id": str(card_type_id)})
        if doc is None:
            raise EntityNotFoundError(f"card_type {card_type_id} not found")
        return MongoCardTypeMapper.to_entity(doc)

    def delete(self, card_type_id: UUID) -> None:
        result = self._col.delete_one({"_id": str(card_type_id)})
        if result.deleted_count == 0:
            raise EntityNotFoundError(f"card_type {card_type_id} not found")

    def exists(self, card_type_id: str) -> bool:
        return self._col.count_documents({"_id": card_type_id}, limit=1) > 0

    def list_all(self) -> list[CardType]:
        return [
            MongoCardTypeMapper.to_entity(doc)
            for doc in self._col.find().sort("action", 1)
        ]

    def find_by_title(self, title: str) -> CardType | None:
        doc = self._col.find_one({"action": title})
        if doc is None:
            return None
        return MongoCardTypeMapper.to_entity(doc)
