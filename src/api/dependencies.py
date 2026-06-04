from collections.abc import Generator
from dataclasses import dataclass
from functools import lru_cache
from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from application.interfaces.card_repository import CardRepository
from application.interfaces.card_type_repository import CardTypeRepository
from application.interfaces.game_repository import GameRepository
from application.interfaces.user_repository import UserRepository
from application.services.access_control import Operation, Resource, has_permission
from application.services.card_image_service import CardImageService
from application.services.card_logic import CardLogic
from application.services.deck_service import DeckService
from application.services.game_service import GameAppService
from application.services.game_state_manager import GameStateManager
from config.config import load_config
from domain.entities import User
from domain.enums import UserRole
from infrastructure.cache.redis_cache import RedisCache
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.storage import MinioImageStorage

config = load_config()


@dataclass(frozen=True)
class CurrentActor:
    user: User | None
    role: UserRole

# ─── PostgreSQL ───────────────────────────────────────────────────────────────

# Создаём PostgreSQL engine только если используется postgres backend
if config.storage_backend == "postgres":
    engine = create_engine(config.database.url, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)
else:
    engine = None  # type: ignore[assignment]
    SessionLocal = None  # type: ignore[assignment]


def get_db() -> Generator[Session, None, None]:
    if SessionLocal is None:
        raise RuntimeError("PostgreSQL is not configured. Set STORAGE_BACKEND=postgres")
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ─── MongoDB ──────────────────────────────────────────────────────────────────


def _get_mongo_db():  # type: ignore[return]
    """Возвращает MongoDB Database или None если не сконфигурирован."""
    if config.mongo is None:
        return None
    from infrastructure.mongo.client import get_mongo_db

    return get_mongo_db(config.mongo)


# ─── Repository factories ─────────────────────────────────────────────────────


def _make_repositories(
    session: Session | None,
) -> tuple[GameRepository, UserRepository, CardRepository, CardTypeRepository]:
    """
    Создаёт репозитории в зависимости от storage_backend в конфиге.
    - "postgres" — SQLAlchemy + PostgreSQL
    - "mongo"    — PyMongo + MongoDB
    """
    backend = config.storage_backend

    if backend == "mongo":
        db = _get_mongo_db()
        if db is None:
            raise RuntimeError(
                "storage_backend=mongo but mongo.url is not configured. "
                "Set MONGO_URL in .env or mongo.url in config.yaml"
            )
        from infrastructure.mongo.repositories.mongo_card_repository import (
            MongoCardRepository,
        )
        from infrastructure.mongo.repositories.mongo_card_type_repository import (
            MongoCardTypeRepository,
        )
        from infrastructure.mongo.repositories.mongo_game_repository import (
            MongoGameRepository,
        )
        from infrastructure.mongo.repositories.mongo_user_repository import (
            MongoUserRepository,
        )

        return (
            MongoGameRepository(db),
            MongoUserRepository(db),
            MongoCardRepository(db),
            MongoCardTypeRepository(db),
        )

    # default: postgres
    if session is None:
        raise RuntimeError("PostgreSQL session is required for postgres backend")

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

    return (
        SqlAlchemyGameRepository(session),
        SqlAlchemyUserRepository(session),
        SqlAlchemyCardRepository(session),
        SqlAlchemyCardTypeRepository(session),
    )


# ─── FastAPI dependencies ─────────────────────────────────────────────────────


@lru_cache(maxsize=1)
def get_image_storage() -> MinioImageStorage:
    return MinioImageStorage(config.minio)


@lru_cache(maxsize=1)
def get_redis_cache() -> RedisCache:
    """Внешний кэш Redis для каталога карт и других read-heavy данных."""
    return RedisCache(
        config.redis.url,
        enabled=config.redis.enabled,
        default_ttl_seconds=config.redis.catalog_ttl_seconds,
    )


def get_db_optional() -> Generator[Session | None, None, None]:
    """Возвращает PostgreSQL сессию только если backend=postgres."""
    if config.storage_backend == "postgres":
        if SessionLocal is None:
            raise RuntimeError("PostgreSQL SessionLocal is not initialized")
        session = SessionLocal()
        try:
            yield session
        finally:
            session.close()
    else:
        yield None


def get_game_service(
    session: Annotated[Session | None, Depends(get_db_optional)],
) -> GameAppService:
    game_repo, user_repo, card_repo, card_type_repo = _make_repositories(session)
    return GameAppService(
        game_repository=game_repo,
        user_repository=user_repo,
        card_logic=CardLogic(),
        deck_service=DeckService(),
        game_state_manager=GameStateManager(),
        card_repository=card_repo,
        card_type_repository=card_type_repo,
        default_market_size=config.game.default_market_size,
    )


def get_card_image_service(
    session: Annotated[Session | None, Depends(get_db_optional)],
) -> CardImageService:
    _, _, card_repo, _ = _make_repositories(session)
    return CardImageService(
        card_repository=card_repo,
        image_storage=get_image_storage(),
        default_image_object=config.minio.default_image_object,
    )


def get_current_actor(
    session: Annotated[Session | None, Depends(get_db_optional)],
    x_user_id: Annotated[UUID | None, Header(alias="X-User-Id")] = None,
) -> CurrentActor:
    if x_user_id is None:
        return CurrentActor(user=None, role=UserRole.GUEST)

    _, user_repo, _, _ = _make_repositories(session)
    try:
        user = user_repo.get(x_user_id)
    except EntityNotFoundError as exc:
        raise HTTPException(status_code=401, detail="Unknown user") from exc

    return CurrentActor(user=user, role=user.role)


def require_permission(resource: Resource, operation: Operation):
    def dependency(
        actor: Annotated[CurrentActor, Depends(get_current_actor)],
    ) -> CurrentActor:
        if not has_permission(actor.role, resource, operation):
            raise HTTPException(status_code=403, detail="Not enough permissions")
        return actor

    return dependency


def require_any_permission(
    permissions: tuple[tuple[Resource, Operation], ...],
):
    def dependency(
        actor: Annotated[CurrentActor, Depends(get_current_actor)],
    ) -> CurrentActor:
        if any(
            has_permission(actor.role, resource, operation)
            for resource, operation in permissions
        ):
            return actor
        raise HTTPException(status_code=403, detail="Not enough permissions")

    return dependency
