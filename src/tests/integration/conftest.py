import pytest
from typing import Generator
from sqlalchemy import create_engine, Engine
from sqlalchemy.orm import Session, sessionmaker

from infrastructure.db.base import Base


@pytest.fixture()
def engine() -> Generator[Engine, None, None]:
    from sqlalchemy.engine import Engine

    engine: Engine = create_engine("sqlite+pysqlite:///:memory:", future=True)
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
