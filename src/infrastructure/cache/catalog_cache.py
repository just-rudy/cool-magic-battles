"""Кэширование ответов API каталога карт (GET /cards, GET /cards/types)."""

from __future__ import annotations

import json

from application.dto.responses import CardResponse, CardTypeResponse
from infrastructure.cache.redis_cache import (
    CATALOG_CARD_TYPES_KEY,
    CATALOG_CARDS_KEY,
    RedisCache,
)


def get_cached_cards(cache: RedisCache) -> list[CardResponse] | None:
    raw = cache.get(CATALOG_CARDS_KEY)
    if raw is None:
        return None
    items = json.loads(raw)
    return [CardResponse.model_validate(item) for item in items]


def set_cached_cards(cache: RedisCache, cards: list[CardResponse]) -> None:
    payload = json.dumps(
        [card.model_dump(mode="json") for card in cards],
        ensure_ascii=False,
    )
    cache.set(CATALOG_CARDS_KEY, payload)


def get_cached_card_types(cache: RedisCache) -> list[CardTypeResponse] | None:
    raw = cache.get(CATALOG_CARD_TYPES_KEY)
    if raw is None:
        return None
    items = json.loads(raw)
    return [CardTypeResponse.model_validate(item) for item in items]


def set_cached_card_types(
    cache: RedisCache, card_types: list[CardTypeResponse]
) -> None:
    payload = json.dumps(
        [ct.model_dump(mode="json") for ct in card_types],
        ensure_ascii=False,
    )
    cache.set(CATALOG_CARD_TYPES_KEY, payload)
