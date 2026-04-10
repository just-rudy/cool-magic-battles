from dataclasses import dataclass
from uuid import UUID


@dataclass
class Card:
    id: UUID
    title: str
    creature: str
    power: int = 1  # effect power
    echo: int = 1  # card buying currency
    cost: int = 3  # card cost in echo
    cool_points: int = 0
