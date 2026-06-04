"""MongoDB implementation of CardRepository."""
from uuid import UUID

from pymongo.database import Database
from pymongo.errors import DuplicateKeyError, PyMongoError

from application.interfaces.card_repository import CardRepository
from domain.entities import Card
from infrastructure.db.exceptions import EntityNotFoundError, PersistenceError
from infrastructure.mongo.mappers.card_mapper import MongoCardMapper


class MongoCardRepository(CardRepository):
    COLLECTION = "cards"

    def __init__(self, db: Database) -> None:  # type: ignore[type-arg]
        self._col = db[self.COLLECTION]
        self._col.create_index("title", unique=True, background=True)

    def save(self, card: Card) -> None:
        doc = MongoCardMapper.to_document(card)
        try:
            self._col.replace_one({"_id": doc["_id"]}, doc, upsert=True)
        except DuplicateKeyError as exc:
            raise PersistenceError(
                "failed to save card: title already exists"
            ) from exc
        except PyMongoError as exc:
            raise PersistenceError("failed to save card") from exc

    def get(self, card_id: UUID) -> Card:
        doc = self._col.find_one({"_id": str(card_id)})
        if doc is None:
            raise EntityNotFoundError(f"card {card_id} not found")
        return MongoCardMapper.to_entity(doc)

    def delete(self, card_id: UUID) -> None:
        result = self._col.delete_one({"_id": str(card_id)})
        if result.deleted_count == 0:
            raise EntityNotFoundError(f"card {card_id} not found")

    def exists(self, card_id: UUID) -> bool:
        return self._col.count_documents({"_id": str(card_id)}, limit=1) > 0

    def list_all(self) -> list[Card]:
        return [
            MongoCardMapper.to_entity(doc)
            for doc in self._col.find().sort("title", 1)
        ]

    def find_by_title(self, title: str) -> Card | None:
        doc = self._col.find_one({"title": title})
        if doc is None:
            return None
        return MongoCardMapper.to_entity(doc)
