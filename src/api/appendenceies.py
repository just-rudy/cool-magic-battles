from typing import Annotated

from application.services.user_service import UserAppService
from core.database import get_db  # Твой генератор сессий
from fastapi import Depends
from sqlalchemy.orm import Session

from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)


def get_user_service(
    session: Annotated[Session, Depends(get_db)],
) -> UserAppService:
    repository = SqlAlchemyUserRepository(session)
    return UserAppService(repository)


# Аналогично для GameService
