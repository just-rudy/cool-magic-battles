from __future__ import annotations

from typing import Any, Iterable
from uuid import UUID


def is_valid_uuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except ValueError:
        return False


def short_id(value: Any, length: int = 8) -> str:
    if value is None:
        return ""
    return str(value)[:length]


def resolve_uuid(value: str) -> UUID:
    try:
        return UUID(value)
    except ValueError as exc:
        raise ValueError(f"invalid uuid: {value}") from exc


def resolve_entity_id(
    raw: str,
    items: Iterable[Any],
    *,
    attr_name: str = "id",
    entity_name: str = "entity",
) -> UUID:
    raw = raw.strip()
    if not raw:
        raise ValueError(f"{entity_name} id is empty")

    try:
        return UUID(raw)
    except ValueError:
        pass

    matches: list[UUID] = []

    for item in items:
        value = getattr(item, attr_name, None)
        if value is None and isinstance(item, dict):
            value = item.get(attr_name)

        if value is None:
            continue

        full = str(value)
        if full.startswith(raw):
            matches.append(UUID(full))

    if not matches:
        raise ValueError(f"{entity_name} with id '{raw}' not found")

    if len(matches) > 1:
        found = ", ".join(str(x)[:8] for x in matches)
        raise ValueError(f"ambiguous {entity_name} id '{raw}', matches: {found}")

    return matches[0]


def resolve_entity_by_attr(
    raw: str,
    items: Iterable[Any],
    *,
    attr_name: str,
    entity_name: str = "entity",
    case_insensitive: bool = True,
) -> UUID:
    raw = raw.strip()
    if not raw:
        raise ValueError(f"{entity_name} {attr_name} is empty")

    matches: list[UUID] = []

    for item in items:
        item_id = getattr(item, "id", None)
        if item_id is None and isinstance(item, dict):
            item_id = item.get("id")

        attr_value = getattr(item, attr_name, None)
        if attr_value is None and isinstance(item, dict):
            attr_value = item.get(attr_name)

        if item_id is None or attr_value is None:
            continue

        left = str(attr_value)
        right = raw

        if case_insensitive:
            left = left.lower()
            right = right.lower()

        if left == right:
            matches.append(UUID(str(item_id)))

    if not matches:
        raise ValueError(f"{entity_name} with {attr_name} '{raw}' not found")

    if len(matches) > 1:
        found = ", ".join(str(x)[:8] for x in matches)
        raise ValueError(
            f"ambiguous {entity_name} {attr_name} '{raw}', matches: {found}"
        )

    return matches[0]
