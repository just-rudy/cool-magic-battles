from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


class SessionFactory:
    def __init__(self, database_url: str, echo: bool = False) -> None:
        self._engine = create_engine(
            database_url,
            future=True,
            echo=echo,
        )
        self._session_maker = sessionmaker(
            bind=self._engine,
            expire_on_commit=False,
            class_=Session,
        )

    @property
    def engine(self) -> Engine:
        return self._engine

    def create_session(self) -> Session:
        return self._session_maker()
