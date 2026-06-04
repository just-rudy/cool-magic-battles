from enum import Enum

from domain.enums import UserRole


class Resource(str, Enum):
    RULES = "rules"
    USERS = "users"
    GAMES = "games"
    PLAYERS = "players"
    CARDS = "cards"
    CARD_TYPES = "card_types"
    IMAGES = "images"
    DECKS = "decks"
    DECK_CARDS = "deck_cards"


class Operation(str, Enum):
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"


CRUD = {
    Operation.CREATE,
    Operation.READ,
    Operation.UPDATE,
    Operation.DELETE,
}

READ_ONLY = {Operation.READ}
CREATE_READ = {Operation.CREATE, Operation.READ}


ROLE_PERMISSIONS: dict[UserRole, dict[Resource, set[Operation]]] = {
    UserRole.GUEST: {
        Resource.RULES: READ_ONLY,
        Resource.CARDS: READ_ONLY,
        Resource.CARD_TYPES: READ_ONLY,
        Resource.IMAGES: READ_ONLY,
    },
    UserRole.AUTHENTICATED: {
        Resource.RULES: READ_ONLY,
        Resource.GAMES: CREATE_READ,
        Resource.PLAYERS: CREATE_READ,
        Resource.CARDS: READ_ONLY,
        Resource.CARD_TYPES: READ_ONLY,
        Resource.IMAGES: READ_ONLY,
    },
    UserRole.PLAYER: {
        Resource.RULES: READ_ONLY,
        Resource.GAMES: CREATE_READ,
        Resource.PLAYERS: CREATE_READ,
        Resource.CARDS: READ_ONLY,
        Resource.CARD_TYPES: READ_ONLY,
        Resource.IMAGES: READ_ONLY,
        Resource.DECKS: {Operation.READ, Operation.UPDATE},
        Resource.DECK_CARDS: {
            Operation.READ,
            Operation.UPDATE,
            Operation.DELETE,
        },
    },
    UserRole.MODERATOR: {
        Resource.RULES: READ_ONLY,
        Resource.USERS: CRUD,
        Resource.GAMES: CRUD,
        Resource.PLAYERS: CRUD,
        Resource.CARDS: READ_ONLY,
        Resource.CARD_TYPES: READ_ONLY,
        Resource.IMAGES: READ_ONLY,
        Resource.DECKS: READ_ONLY,
        Resource.DECK_CARDS: READ_ONLY,
    },
    UserRole.MASTER: {
        Resource.RULES: READ_ONLY,
        Resource.USERS: CRUD,
        Resource.GAMES: CRUD,
        Resource.PLAYERS: CRUD,
        Resource.CARDS: CRUD,
        Resource.CARD_TYPES: CRUD,
        Resource.IMAGES: CRUD,
        Resource.DECKS: READ_ONLY,
        Resource.DECK_CARDS: READ_ONLY,
    },
}


def has_permission(
    role: UserRole,
    resource: Resource,
    operation: Operation,
) -> bool:
    return operation in ROLE_PERMISSIONS.get(role, {}).get(resource, set())
