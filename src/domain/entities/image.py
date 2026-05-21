from dataclasses import dataclass
from uuid import UUID


@dataclass
class Image:
    id: UUID
    title: str
    file: str | None = None
