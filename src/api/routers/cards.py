from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from api.dependencies import get_card_image_service, get_db
from api.routers.games import build_card_response
from application.dto.requests import UpdateCardImageRequest
from application.dto.responses import CardResponse
from application.interfaces.card_repository import CardRepository
from application.services.card_image_service import CardImageService
from infrastructure.db.exceptions import EntityNotFoundError
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)

router = APIRouter()


def get_card_repository(
    session: Annotated[Session, Depends(get_db)],
) -> CardRepository:
    return SqlAlchemyCardRepository(session)


@router.get("", response_model=list[CardResponse])
def list_cards(
    repository: Annotated[CardRepository, Depends(get_card_repository)],
    image_service: Annotated[CardImageService, Depends(get_card_image_service)],
) -> list[CardResponse]:
    return [
        build_card_response(card, image_service) for card in repository.list_all()
    ]


@router.get("/{card_id}", response_model=CardResponse)
def get_card(
    card_id: UUID,
    repository: Annotated[CardRepository, Depends(get_card_repository)],
    image_service: Annotated[CardImageService, Depends(get_card_image_service)],
) -> CardResponse:
    try:
        return build_card_response(repository.get(card_id), image_service)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex


@router.post("/{card_id}/image", response_model=CardResponse)
def upload_card_image(
    card_id: UUID,
    request: UpdateCardImageRequest,
    service: Annotated[CardImageService, Depends(get_card_image_service)],
) -> CardResponse:
    try:
        card = service.upload_card_image(
            card_id=card_id,
            title=request.title,
            filename=request.filename,
            content_base64=request.content_base64,
            content_type=request.content_type,
        )
        return build_card_response(card, service)
    except EntityNotFoundError as ex:
        raise HTTPException(status_code=404, detail=str(ex)) from ex
    except ValueError as ex:
        raise HTTPException(status_code=400, detail=str(ex)) from ex
