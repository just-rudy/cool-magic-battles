"""initial schema

Revision ID: 001_initial
Revises:
Create Date: 2026-05-15

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("username", sa.String(length=50), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username", name="uq_user_username"),
    )
    op.create_table(
        "games",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("host_user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.Column("cur_turn", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cur_player_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.ForeignKeyConstraint(["host_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("title", sa.String(length=200), nullable=False),
        sa.Column("creature", sa.String(length=100), nullable=False),
        sa.Column("power", sa.Integer(), nullable=False, server_default="2"),
        sa.Column("echo", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("cost", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("cool_points", sa.Integer(), nullable=False, server_default="0"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "players",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("nickname", sa.String(length=50), nullable=False),
        sa.Column("turn_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("health", sa.Integer(), nullable=False, server_default="20"),
        sa.Column("base_echo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cur_echo", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("hand_size", sa.Integer(), nullable=False, server_default="5"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("game_id", "user_id", name="uq_players_game_user"),
    )
    op.create_table(
        "decks",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=50), nullable=False),
        sa.Column("game_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("if_open", sa.Boolean(), nullable=False, server_default="false"),
        sa.ForeignKeyConstraint(["game_id"], ["games.id"]),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "deck_cards",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("deck_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("card_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(["card_id"], ["cards.id"]),
        sa.ForeignKeyConstraint(["deck_id"], ["decks.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("deck_id", "position", name="uq_deck_position"),
    )


def downgrade() -> None:
    op.drop_table("deck_cards")
    op.drop_table("decks")
    op.drop_table("players")
    op.drop_table("cards")
    op.drop_table("games")
    op.drop_table("users")
