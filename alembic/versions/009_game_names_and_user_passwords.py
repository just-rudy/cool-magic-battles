"""game names and user passwords

Revision ID: 009_game_names_passwords
Revises: 008_user_roles
Create Date: 2026-05-16

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "009_game_names_passwords"
down_revision: str | None = "008_user_roles"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "games",
        sa.Column("name", sa.String(length=100), nullable=False, server_default=""),
    )
    op.execute(
        """
        UPDATE games
        SET name = 'game-' || substr(replace(id::text, '-', ''), 1, 8)
        WHERE name = '' OR name IS NULL
        """
    )
    op.create_unique_constraint("uq_games_name", "games", ["name"])

    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "password_hash")
    op.drop_constraint("uq_games_name", "games", type_="unique")
    op.drop_column("games", "name")
