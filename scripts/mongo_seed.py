#!/usr/bin/env python3
"""Заполняет MongoDB тестовыми данными (пользователи, типы карт, карты).

Использование:
    STORAGE_BACKEND=mongo PYTHONPATH=src python scripts/mongo_seed.py
    # или с явным URL:
    MONGO_URL=mongodb://localhost:27017 PYTHONPATH=src python scripts/mongo_seed.py
"""
from __future__ import annotations

import sys
from pathlib import Path
from uuid import uuid4

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from application.services.card_factory import (  # noqa: E402
    generate_cards,
    list_card_types,
)
from config.config import load_config  # noqa: E402
from domain.entities import User  # noqa: E402
from infrastructure.mongo.client import get_mongo_db  # noqa: E402
from infrastructure.mongo.repositories.mongo_card_repository import (  # noqa: E402
    MongoCardRepository,
)
from infrastructure.mongo.repositories.mongo_card_type_repository import (  # noqa: E402
    MongoCardTypeRepository,
)
from infrastructure.mongo.repositories.mongo_user_repository import (  # noqa: E402
    MongoUserRepository,
)


def main() -> int:
    config = load_config()

    if config.mongo is None:
        print("ERROR: mongo.url is not configured.")
        print("Set MONGO_URL in .env or mongo.url in config.yaml")
        return 1

    db = get_mongo_db(config.mongo)
    print(f"Connected to MongoDB: {config.mongo.url} / {config.mongo.database}")

    # ── Users ──────────────────────────────────────────────────────────────────
    user_repo = MongoUserRepository(db)
    seed_users = [
        User(id=uuid4(), username="gandalf"),
        User(id=uuid4(), username="saruman"),
        User(id=uuid4(), username="radagast"),
    ]
    for user in seed_users:
        existing = user_repo.get_by_username(user.username)
        if existing:
            print(f"  skip  user '{user.username}' (already exists)")
            continue
        user_repo.save(user)
        print(f"  add   user '{user.username}'  id={user.id}")

    # ── Card types ─────────────────────────────────────────────────────────────
    ct_repo = MongoCardTypeRepository(db)
    existing_ct_ids = {ct.id for ct in ct_repo.list_all()}
    added_ct = 0
    for card_type in list_card_types():
        if card_type.id in existing_ct_ids:
            continue
        ct_repo.save(card_type)
        added_ct += 1
    print(f"  add   {added_ct} card types ({len(list_card_types())} total)")

    # ── Cards ──────────────────────────────────────────────────────────────────
    card_repo = MongoCardRepository(db)
    existing_titles = {c.title for c in card_repo.list_all()}
    target = 100
    current = len(existing_titles)
    print(f"Current cards in MongoDB: {current}")

    if current >= target:
        print(f"  skip  card seed (already have {current} cards)")
    else:
        all_cards = generate_cards(target)
        new_cards = [
            c for c in all_cards if c.title not in existing_titles
        ][: target - current]
        for card in new_cards:
            card_repo.save(card)
        print(f"  add   {len(new_cards)} cards")

    print("MongoDB seed complete.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
