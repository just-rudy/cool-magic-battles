import base64
import binascii
from pathlib import PurePosixPath
from uuid import UUID

from application.interfaces.card_repository import CardRepository
from application.interfaces.image_storage import ImageStorage
from domain.entities import Image


class CardImageService:
    def __init__(self, card_repository: CardRepository, image_storage: ImageStorage) -> None:
        self._card_repository = card_repository
        self._image_storage = image_storage

    def upload_card_image(
        self,
        card_id: UUID,
        *,
        title: str | None,
        filename: str,
        content_base64: str,
        content_type: str,
    ):
        if not filename.strip():
            raise ValueError("filename must not be empty")

        try:
            content = base64.b64decode(content_base64, validate=True)
        except (binascii.Error, ValueError) as err:
            raise ValueError("image content must be valid base64") from err

        if not content:
            raise ValueError("image content must not be empty")

        card = self._card_repository.get(card_id)
        if card.image is None:
            raise ValueError("card image metadata must exist before upload")

        object_name = self._build_object_name(card_id, filename)
        previous_object_name = card.image.file
        stored_object_name = self._image_storage.upload_bytes(
            object_name=object_name,
            content=content,
            content_type=content_type,
        )

        card.image = Image(
            id=card.image_id,
            title=title.strip() if title and title.strip() else card.title,
            file=stored_object_name,
        )

        self._card_repository.save(card)

        if previous_object_name and previous_object_name != stored_object_name:
            self._image_storage.remove_object(previous_object_name)

        return self._card_repository.get(card_id)

    def get_image_url(self, object_name: str | None) -> str | None:
        if not object_name:
            return None
        return self._image_storage.get_download_url(object_name)

    def _build_object_name(self, card_id: UUID, filename: str) -> str:
        clean_filename = PurePosixPath(filename).name
        return f"cards/{card_id}/{clean_filename}"
