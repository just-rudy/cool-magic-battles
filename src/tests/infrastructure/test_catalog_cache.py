from uuid import uuid4

from application.dto.responses import CardResponse, CardTypeResponse, ImageResponse
from infrastructure.cache.catalog_cache import (
    get_cached_card_types,
    get_cached_cards,
    set_cached_card_types,
    set_cached_cards,
)
from infrastructure.cache.redis_cache import RedisCache


def test_catalog_cache_roundtrip_without_redis() -> None:
    cache = RedisCache("redis://localhost:6379/0", enabled=False)

    card = CardResponse(
        id=uuid4(),
        title="Test",
        creature="Wizard",
        image_id=uuid4(),
        image=ImageResponse(
            id=uuid4(),
            title="img",
            file="cards/test.png",
            url="http://test.local/x.png",
        ),
        power=2,
        echo=1,
        cost=3,
        cool_points=1,
        card_type=None,
    )
    set_cached_cards(cache, [card])
    assert get_cached_cards(cache) is None

    card_type = CardTypeResponse(
        id=uuid4(),
        action="attack",
        usage_pattern="reg",
        color="red",
    )
    set_cached_card_types(cache, [card_type])
    assert get_cached_card_types(cache) is None
