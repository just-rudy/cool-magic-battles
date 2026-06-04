"""add unique constraint on cards.title

Revision ID: 006_unique_cards_title
Revises: 005_card_images
Create Date: 2026-05-22

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "006_unique_cards_title"
down_revision: str | None = "005_card_images"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Удаляем дубликаты: оставляем запись с наименьшим id (лексикографически),
    # остальные удаляем вместе с их deck_cards.
    op.execute(
        sa.text(
            """
            DELETE FROM deck_cards
            WHERE card_id IN (
                SELECT id FROM cards
                WHERE id NOT IN (
                    SELECT DISTINCT ON (title) id
                    FROM cards
                    ORDER BY title, id
                )
            )
            """
        )
    )
    op.execute(
        sa.text(
            """
            DELETE FROM cards
            WHERE id NOT IN (
                SELECT DISTINCT ON (title) id
                FROM cards
                ORDER BY title, id
            )
            """
        )
    )

    op.create_unique_constraint("uq_cards_title", "cards", ["title"])


def downgrade() -> None:
    op.drop_constraint("uq_cards_title", "cards", type_="unique")
