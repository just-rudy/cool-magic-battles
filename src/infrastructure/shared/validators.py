from uuid import UUID


def if_uuid_str(value: str) -> bool:
    try:
        return str(UUID(value)) == value
    except ValueError:
        return False
