"""add pending attack fields to games table

Revision ID: 007_pending_attack
Revises: 006_unique_cards_title
Create Date: 2026-05-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "007_pending_attack"
down_revision: str | None = "006_unique_cards_title"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "games",
        sa.Column("pending_attacker_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "games",
        sa.Column("pending_defender_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column(
        "games", sa.Column("pending_damage", sa.Integer(), nullable=True)
    )


def downgrade() -> None:
    op.drop_column("games", "pending_damage")
    op.drop_column("games", "pending_defender_id")
    op.drop_column("games", "pending_attacker_id")
