from application.services.access_control import Operation, Resource, has_permission
from domain.enums import UserRole


def test_guest_can_read_cards_and_rules_only() -> None:
    assert has_permission(UserRole.GUEST, Resource.CARDS, Operation.READ)
    assert has_permission(UserRole.GUEST, Resource.RULES, Operation.READ)
    assert not has_permission(UserRole.GUEST, Resource.GAMES, Operation.READ)


def test_authenticated_user_can_create_games() -> None:
    assert has_permission(
        UserRole.AUTHENTICATED,
        Resource.GAMES,
        Operation.CREATE,
    )
    assert not has_permission(
        UserRole.AUTHENTICATED,
        Resource.USERS,
        Operation.DELETE,
    )


def test_player_can_update_decks() -> None:
    assert has_permission(UserRole.PLAYER, Resource.DECKS, Operation.UPDATE)
    assert has_permission(UserRole.PLAYER, Resource.DECK_CARDS, Operation.DELETE)


def test_moderator_can_manage_users_and_games() -> None:
    assert has_permission(UserRole.MODERATOR, Resource.USERS, Operation.DELETE)
    assert has_permission(UserRole.MODERATOR, Resource.GAMES, Operation.UPDATE)
    assert not has_permission(UserRole.MODERATOR, Resource.CARDS, Operation.UPDATE)


def test_master_can_manage_card_catalog() -> None:
    assert has_permission(UserRole.MASTER, Resource.CARDS, Operation.UPDATE)
    assert has_permission(UserRole.MASTER, Resource.CARD_TYPES, Operation.DELETE)
    assert has_permission(UserRole.MASTER, Resource.IMAGES, Operation.CREATE)
