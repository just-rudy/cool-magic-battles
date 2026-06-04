"""MongoDB client factory."""
from functools import lru_cache

from pymongo import MongoClient
from pymongo.database import Database

from config.config import MongoConfig


@lru_cache(maxsize=1)
def get_mongo_client(url: str) -> MongoClient:  # type: ignore[type-arg]
    return MongoClient(url)


def get_mongo_db(config: MongoConfig) -> Database:  # type: ignore[type-arg]
    client = get_mongo_client(config.url)
    return client[config.database]
