"""create card types table

Revision ID: 003_create_card_types
Revises: 002_add_game_winner
Create Date: 2026-05-18

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "003_create_card_types"
down_revision: str | None = "002_add_game_winner"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "card_types",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("action", sa.String(length=50), nullable=False),
        sa.Column("usage_pattern", sa.String(length=50), nullable=False),
        sa.Column("if_permanent", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("color", sa.String(length=50), nullable=False, server_default="red"),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("card_types")
