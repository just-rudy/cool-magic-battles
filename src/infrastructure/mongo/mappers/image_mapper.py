from domain.entities import Image
from infrastructure.db.models import ImageModel


class ImageMapper:
    @staticmethod
    def to_domain(model: ImageModel) -> Image:
        return Image(
            id=model.id,
            title=model.title,
            file=model.file,
        )

    @staticmethod
    def to_model(entity: Image) -> ImageModel:
        return ImageModel(
            id=entity.id,
            title=entity.title,
            file=entity.file,
        )
