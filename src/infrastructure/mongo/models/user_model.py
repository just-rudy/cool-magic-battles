"""MongoDB document model for User."""
from typing import TypedDict


class UserDocument(TypedDict):
    _id: str  # UUID as string
    username: str
    role: str
