"""add user roles and database grants

Revision ID: 008_user_roles
Revises: 007_pending_attack
Create Date: 2026-05-28

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

revision: str = "008_user_roles"
down_revision: str | None = "007_pending_attack"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


APP_ROLES = (
    "cmb_guest",
    "cmb_authenticated_user",
    "cmb_player",
    "cmb_moderator",
    "cmb_master",
)


def _roles_sql() -> str:
    return "\n".join(
        f"""
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1 FROM pg_roles WHERE rolname = '{role}'
            ) THEN
                CREATE ROLE {role} NOLOGIN;
            END IF;
        END
        $$;
        """
        for role in APP_ROLES
    )


def _can_manage_pg_roles(connection: sa.Connection) -> bool:
    """CREATE ROLE / GRANT need superuser or CREATEROLE (e.g. Docker cmb user)."""
    row = connection.execute(
        text(
            """
            SELECT COALESCE(rolsuper, false) OR COALESCE(rolcreaterole, false)
            FROM pg_roles
            WHERE rolname = current_user
            """
        )
    ).scalar()
    return bool(row)


def _apply_pg_role_grants() -> None:
    op.execute(_roles_sql())
    op.execute(f"GRANT USAGE ON SCHEMA public TO {', '.join(APP_ROLES)}")

    all_roles = ", ".join(APP_ROLES)
    op.execute(f"GRANT SELECT ON cards, card_types, images TO {all_roles}")

    op.execute(
        """
        GRANT SELECT, INSERT ON games, players
            TO cmb_authenticated_user, cmb_player;
        GRANT SELECT, UPDATE ON decks TO cmb_player;
        GRANT SELECT, UPDATE, DELETE ON deck_cards TO cmb_player;

        GRANT SELECT, INSERT, UPDATE, DELETE
            ON users, games, players
            TO cmb_moderator, cmb_master;
        GRANT SELECT ON decks, deck_cards TO cmb_moderator, cmb_master;

        GRANT INSERT, UPDATE, DELETE
            ON cards, card_types, images
            TO cmb_master;
        """
    )


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "role",
            sa.String(length=32),
            nullable=False,
            server_default="authenticated",
        ),
    )
    op.create_check_constraint(
        "ck_users_role",
        "users",
        "role in ('guest', 'authenticated', 'player', 'moderator', 'master')",
    )

    bind = op.get_bind()
    if bind.dialect.name != "postgresql":
        return

    if not _can_manage_pg_roles(bind):
        # Локальный владелец БД без CREATEROLE: RBAC в приложении, без PG-ролей.
        return

    _apply_pg_role_grants()


def downgrade() -> None:
    bind = op.get_bind()
    if bind.dialect.name == "postgresql" and _can_manage_pg_roles(bind):
        op.execute(
            """
            REVOKE ALL PRIVILEGES ON
                users, games, players, cards, card_types, images, decks, deck_cards
                FROM cmb_guest, cmb_authenticated_user, cmb_player,
                     cmb_moderator, cmb_master;
            REVOKE USAGE ON SCHEMA public
                FROM cmb_guest, cmb_authenticated_user, cmb_player,
                     cmb_moderator, cmb_master;
            """
        )
        for role in APP_ROLES:
            op.execute(f"DROP ROLE IF EXISTS {role}")

    op.drop_constraint("ck_users_role", "users", type_="check")
    op.drop_column("users", "role")
