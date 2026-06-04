"""Fixtures for MongoDB repository tests using mongomock."""
import mongomock
import pytest


@pytest.fixture
def mongo_db():
    """In-memory MongoDB database via mongomock."""
    client = mongomock.MongoClient()
    return client["test_db"]
