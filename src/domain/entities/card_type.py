from dataclasses import dataclass
from uuid import UUID

from domain.enums import CardAction, UsePattern


@dataclass
class CardType:
    id: UUID
    action: CardAction = CardAction.ATTACK
    usage_pattern: UsePattern = UsePattern.REG
    if_permanent: bool = False
    color: str = "red"
