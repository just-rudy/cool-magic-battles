from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from api.dependencies import get_db
from application.controllers.user_controller import UserController
from application.dto.responses import UserResponse
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)

router = APIRouter()


class RegisterUserRequest(BaseModel):
    username: str


def get_user_controller(
    session: Annotated[Session, Depends(get_db)],
) -> UserController:
    return UserController(SqlAlchemyUserRepository(session))


@router.post("/register", response_model=UserResponse)
def register_user(
    request: RegisterUserRequest,
    controller: Annotated[UserController, Depends(get_user_controller)],
) -> UserResponse:
    try:
        user = controller.register_user(request.username)
    except ValueError as ex:
        message = str(ex)
        status = 409 if "already taken" in message else 400
        raise HTTPException(status_code=status, detail=message) from ex

    return UserResponse(id=user.id, username=user.username)


@router.post("/login", response_model=UserResponse)
def login_user(
    request: RegisterUserRequest,
    controller: Annotated[UserController, Depends(get_user_controller)],
) -> UserResponse:
    try:
        user = controller.login_user(request.username)
    except ValueError as ex:
        message = str(ex)
        status = 404 if "not found" in message else 400
        raise HTTPException(status_code=status, detail=message) from ex

    return UserResponse(id=user.id, username=user.username)


@router.get("", response_model=list[UserResponse])
def list_users(
    controller: Annotated[UserController, Depends(get_user_controller)],
) -> list[UserResponse]:
    from uuid import UUID

    return [
        UserResponse(id=UUID(str(user["id"])), username=str(user["username"]))
        for user in controller.list_users()
    ]


@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    controller: Annotated[UserController, Depends(get_user_controller)],
) -> UserResponse:
    from uuid import UUID

    try:
        user = controller.show_user(UUID(user_id))
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail="User not found") from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex

    from uuid import UUID

    return UserResponse(id=UUID(str(user["id"])), username=str(user["username"]))
