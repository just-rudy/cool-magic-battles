from __future__ import annotations

from datetime import timedelta
from io import BytesIO
from types import TracebackType
from typing import Any
from urllib.parse import quote

from application.interfaces.image_storage import ImageStorage
from config.config import MinioConfig


class MinioImageStorage(ImageStorage):
    def __init__(self, config: MinioConfig) -> None:
        self._config = config
        self._client = self._build_client()

        if self._config.auto_create_bucket:
            self.ensure_bucket_exists()

    def ensure_bucket_exists(self) -> None:
        if not self._client.bucket_exists(self._config.bucket):
            self._client.make_bucket(self._config.bucket)

    def upload_bytes(
        self,
        object_name: str,
        content: bytes,
        content_type: str,
    ) -> str:
        self._client.put_object(
            bucket_name=self._config.bucket,
            object_name=object_name,
            data=BytesIO(content),
            length=len(content),
            content_type=content_type,
        )
        return object_name

    def remove_object(self, object_name: str) -> None:
        self._client.remove_object(self._config.bucket, object_name)

    def get_download_url(self, object_name: str) -> str:
        if self._config.public_base_url:
            base_url = self._config.public_base_url.rstrip("/")
            return (
                f"{base_url}/{quote(self._config.bucket)}/{quote(object_name, safe='/')}"
            )

        return self._client.presigned_get_object(
            self._config.bucket,
            object_name,
            expires=timedelta(seconds=self._config.presign_ttl_seconds),
        )

    def _build_client(self) -> Any:
        try:
            from minio import Minio
        except ImportError as err:
            raise RuntimeError(
                "MinIO client is not installed. Add the 'minio' package to the environment."
            ) from err

        return Minio(
            endpoint=self._config.endpoint,
            access_key=self._config.access_key,
            secret_key=self._config.secret_key,
            secure=self._config.secure,
        )
