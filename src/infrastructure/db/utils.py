from sqlalchemy.engine import Engine

from infrastructure.db.base import Base


def create_tables(engine: Engine) -> None:
    Base.metadata.create_all(bind=engine)


def drop_tables(engine: Engine) -> None:
    Base.metadata.drop_all(bind=engine)
