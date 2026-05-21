"""add card type id to cards

Revision ID: 004_add_card_type_id_to_cards
Revises: 003_create_card_types
Create Date: 2026-05-19

"""

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "004_add_card_type_id_to_cards"
down_revision: str | None = "003_create_card_types"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_CARD_TYPE_ID = UUID("6c9097de-cd28-5eab-975b-8a7de384fd6f")


def upgrade() -> None:
    op.add_column(
        "cards",
        sa.Column("card_type_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.execute(
        sa.text(
            """
            INSERT INTO card_types (id, action, usage_pattern, if_permanent, color)
            VALUES (:card_type_id, 'attack', 'reg', false, 'red')
            ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(
            sa.bindparam(
                "card_type_id",
                value=DEFAULT_CARD_TYPE_ID,
                type_=postgresql.UUID(as_uuid=True),
            )
        )
    )
    op.execute(
        sa.text(
            """
            UPDATE cards
            SET card_type_id = :card_type_id
            WHERE card_type_id IS NULL
            """
        ).bindparams(
            sa.bindparam(
                "card_type_id",
                value=DEFAULT_CARD_TYPE_ID,
                type_=postgresql.UUID(as_uuid=True),
            )
        )
    )
    op.alter_column(
        "cards",
        "card_type_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_cards_card_type_id_card_types",
        "cards",
        "card_types",
        ["card_type_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_cards_card_type_id_card_types", "cards", type_="foreignkey")
    op.drop_column("cards", "card_type_id")
