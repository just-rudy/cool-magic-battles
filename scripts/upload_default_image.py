#!/usr/bin/env python3
"""Загружает assets/default-image.png в MinIO как дефолтное изображение карт."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

DEFAULT_IMAGE_PATH = ROOT / "assets" / "cards" / "default-image.png"
DEFAULT_OBJECT_NAME = "cards/default.png"


def main() -> int:
    if not DEFAULT_IMAGE_PATH.exists():
        print(f"File not found: {DEFAULT_IMAGE_PATH}", file=sys.stderr)
        return 1

    from config.config import load_config
    from infrastructure.storage.minio_image_storage import MinioImageStorage

    config = load_config()
    storage = MinioImageStorage(config.minio)

    content = DEFAULT_IMAGE_PATH.read_bytes()
    stored = storage.upload_bytes(
        object_name=DEFAULT_OBJECT_NAME,
        content=content,
        content_type="image/png",
    )
    print(f"Uploaded: {stored}")

    url = storage.get_download_url(stored)
    print(f"URL: {url}")

    if config.minio.default_image_object != DEFAULT_OBJECT_NAME:
        print(
            f"\nWarning: config.minio.default_image_object = "
            f"'{config.minio.default_image_object}', "
            f"expected '{DEFAULT_OBJECT_NAME}'.\n"
            f"Update minio.default_image_object in config.yaml or "
            f"MINIO_DEFAULT_IMAGE_OBJECT in .env."
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
