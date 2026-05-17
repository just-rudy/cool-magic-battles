"""add winner to games

Revision ID: 002_add_game_winner
Revises: 001_initial
Create Date: 2026-05-15

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "002_add_game_winner"
down_revision: str | None = "001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "games",
        sa.Column("winner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_games_winner_id_players",
        "games",
        "players",
        ["winner_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_games_winner_id_players", "games", type_="foreignkey")
    op.drop_column("games", "winner_id")
