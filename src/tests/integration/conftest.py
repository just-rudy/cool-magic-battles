from collections.abc import Generator

import pytest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker

import infrastructure.db.models  # noqa: F401 — register ORM tables
from infrastructure.db.base import Base


@pytest.fixture()
def engine() -> Generator[Engine, None, None]:
    engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
    Base.metadata.create_all(bind=engine)
    try:
        yield engine
    finally:
        Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def session(engine: Engine) -> Generator[Session, None, None]:
    SessionLocal = sessionmaker(
        bind=engine,
        expire_on_commit=False,
        class_=Session,
    )
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
