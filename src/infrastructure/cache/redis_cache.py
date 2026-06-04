"""Внешний кэш на Redis (in-memory СУБД) для снижения нагрузки на PostgreSQL."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import redis

logger = logging.getLogger(__name__)


class RedisCache:
    """Тонкая обёртка над Redis: get/set/delete с graceful fallback при недоступности."""

    def __init__(
        self,
        url: str,
        *,
        enabled: bool = True,
        default_ttl_seconds: int = 300,
    ) -> None:
        self._enabled = enabled
        self._default_ttl = default_ttl_seconds
        self._client: redis.Redis | None = None

        if not enabled:
            return

        try:
            import redis as redis_lib

            self._client = redis_lib.Redis.from_url(
                url,
                decode_responses=True,
                socket_connect_timeout=2,
            )
            self._client.ping()
            logger.info("Redis cache connected: %s", url.split("@")[-1])
        except Exception as exc:  # noqa: BLE001 — fallback без Redis
            logger.warning("Redis unavailable, cache disabled: %s", exc)
            self._client = None

    @property
    def available(self) -> bool:
        return self._client is not None

    def get(self, key: str) -> str | None:
        if self._client is None:
            return None
        try:
            return self._client.get(key)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis GET failed for %s: %s", key, exc)
            return None

    def set(
        self,
        key: str,
        value: str,
        ttl_seconds: int | None = None,
    ) -> None:
        if self._client is None:
            return
        try:
            ttl = ttl_seconds if ttl_seconds is not None else self._default_ttl
            self._client.setex(key, ttl, value)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis SET failed for %s: %s", key, exc)

    def delete(self, *keys: str) -> None:
        if self._client is None or not keys:
            return
        try:
            self._client.delete(*keys)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Redis DELETE failed: %s", exc)


# Ключи кэша каталога карт (внешнее кэширование справочных данных).
CATALOG_CARDS_KEY = "cmb:catalog:cards:v1"
CATALOG_CARD_TYPES_KEY = "cmb:catalog:card_types:v1"


def invalidate_catalog_cache(cache: RedisCache) -> None:
    """Сброс кэша после изменения каталога мастером."""
    cache.delete(CATALOG_CARDS_KEY, CATALOG_CARD_TYPES_KEY)
