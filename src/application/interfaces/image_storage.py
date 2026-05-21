from abc import ABC, abstractmethod


class ImageStorage(ABC):
    @abstractmethod
    def ensure_bucket_exists(self) -> None:
        raise NotImplementedError

    @abstractmethod
    def upload_bytes(
        self,
        object_name: str,
        content: bytes,
        content_type: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def remove_object(self, object_name: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_download_url(self, object_name: str) -> str:
        raise NotImplementedError
