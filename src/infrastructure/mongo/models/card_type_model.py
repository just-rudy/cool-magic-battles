"""MongoDB document model for CardType."""
from typing import TypedDict


class CardTypeDocument(TypedDict):
    _id: str  # UUID as string
    action: str  # CardAction.value
    usage_pattern: str  # UsePattern.value
    if_permanent: bool
    color: str
