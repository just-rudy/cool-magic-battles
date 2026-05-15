from fastapi import Depends
from sqlalchemy.orm import Session
from core.database import get_db  # Твой генератор сессий
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from application.services.user_service import UserAppService


def get_user_service(session: Session = Depends(get_db)) -> UserAppService:
    repository = SqlAlchemyUserRepository(session)
    return UserAppService(repository)


# Аналогично для GameService
