"""sync card type colors by action

Revision ID: 010_sync_card_type_colors
Revises: 009_game_names_passwords
Create Date: 2026-06-01

"""

from collections.abc import Sequence

from alembic import op

revision: str = "010_sync_card_type_colors"
down_revision: str | None = "009_game_names_passwords"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

_ACTION_COLORS = {
    "attack": "red",
    "heal": "green",
    "draw": "purple",
    "defense": "blue",
    "hand_buff": "yellow",
    "echo_buff": "pink",
}


def upgrade() -> None:
    for action, color in _ACTION_COLORS.items():
        op.execute(
            f"UPDATE card_types SET color = '{color}' WHERE action = '{action}'"
        )


def downgrade() -> None:
    pass
