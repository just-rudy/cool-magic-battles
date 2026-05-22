"""add images table and image id to cards

Revision ID: 005_card_images
Revises: 004_add_card_type_id_to_cards
Create Date: 2026-05-21

"""

from collections.abc import Sequence
from uuid import UUID

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "005_card_images"
down_revision: str | None = "004_add_card_type_id_to_cards"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

DEFAULT_IMAGE_ID = UUID("8156540c-f8aa-5f2a-aef6-3f2cca36bf45")


def upgrade() -> None:
    op.create_table(
        "images",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("file", sa.String(length=500), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )

    op.add_column(
        "cards",
        sa.Column("image_id", postgresql.UUID(as_uuid=True), nullable=True),
    )

    op.execute(
        sa.text(
            """
            INSERT INTO images (id, title, file)
            VALUES (:image_id, 'Default card image', 'cards/default.png')
            ON CONFLICT (id) DO NOTHING
            """
        ).bindparams(
            sa.bindparam(
                "image_id",
                value=DEFAULT_IMAGE_ID,
                type_=postgresql.UUID(as_uuid=True),
            )
        )
    )

    op.execute(
        sa.text(
            """
            UPDATE cards
            SET image_id = :image_id
            WHERE image_id IS NULL
            """
        ).bindparams(
            sa.bindparam(
                "image_id",
                value=DEFAULT_IMAGE_ID,
                type_=postgresql.UUID(as_uuid=True),
            )
        )
    )

    op.alter_column(
        "cards",
        "image_id",
        existing_type=postgresql.UUID(as_uuid=True),
        nullable=False,
    )
    op.create_foreign_key(
        "fk_cards_image_id_images",
        "cards",
        "images",
        ["image_id"],
        ["id"],
    )


def downgrade() -> None:
    op.drop_constraint("fk_cards_image_id_images", "cards", type_="foreignkey")
    op.drop_column("cards", "image_id")
    op.drop_table("images")
