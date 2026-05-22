from collections.abc import Generator
from functools import lru_cache
from typing import Annotated

from fastapi import Depends
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.services.card_image_service import CardImageService
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_service import GameAppService
from application.services.game_state_manager import GameStateManager
from config.config import load_config
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)
from infrastructure.db.repositories.sqlalchemy_card_type_repository import (
    SqlAlchemyCardTypeRepository,
)
from infrastructure.db.repositories.sqlalchemy_game_repository import (
    SqlAlchemyGameRepository,
)
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from infrastructure.storage import MinioImageStorage

config = load_config()

engine = create_engine(config.database.url, future=True)

SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def get_db() -> Generator[Session, None, None]:
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


@lru_cache(maxsize=1)
def get_image_storage() -> MinioImageStorage:
    return MinioImageStorage(config.minio)


def get_game_service(
    session: Annotated[Session, Depends(get_db)],
) -> GameAppService:
    return GameAppService(
        game_repository=SqlAlchemyGameRepository(session),
        user_repository=SqlAlchemyUserRepository(session),
        card_logic=CardLogic(),
        deck_service=DeckService(),
        game_state_manager=GameStateManager(),
        card_repository=SqlAlchemyCardRepository(session),
        card_type_repository=SqlAlchemyCardTypeRepository(session),
        default_market_size=config.game.default_market_size,
    )


def get_card_image_service(
    session: Annotated[Session, Depends(get_db)],
) -> CardImageService:
    return CardImageService(
        card_repository=SqlAlchemyCardRepository(session),
        image_storage=get_image_storage(),
        default_image_object=config.minio.default_image_object,
    )
