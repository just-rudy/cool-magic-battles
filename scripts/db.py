#!/usr/bin/env python3
"""Управление БД: миграции Alembic и тестовые данные."""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"


def _alembic_executable() -> str:
    """CLI alembic из venv; не использовать python -m alembic — конфликт с ./alembic/."""  # noqa: E501
    venv_alembic = Path(sys.executable).resolve().parent / "alembic"
    if venv_alembic.is_file():
        return str(venv_alembic)
    found = shutil.which("alembic")
    if found:
        return found
    raise RuntimeError("alembic not found. Install: pip install alembic")


def _run_alembic(args: list[str]) -> int:
    env = {**os.environ, "PYTHONPATH": str(SRC)}
    result = subprocess.run(
        [_alembic_executable(), *args],
        cwd=ROOT,
        env=env,
        check=False,
    )
    return result.returncode


def cmd_upgrade(_: argparse.Namespace) -> int:
    return _run_alembic(["upgrade", "head"])


def cmd_downgrade(args: argparse.Namespace) -> int:
    target = args.revision or "-1"
    return _run_alembic(["downgrade", target])


def cmd_revision(args: argparse.Namespace) -> int:
    cmd = ["revision", "-m", args.message]
    if args.autogenerate:
        cmd.append("--autogenerate")
    return _run_alembic(cmd)


def cmd_current(_: argparse.Namespace) -> int:
    return _run_alembic(["current"])


def cmd_stamp(_: argparse.Namespace) -> int:
    return _run_alembic(["stamp", "head"])


def _make_session_factory():
    sys.path.insert(0, str(SRC))

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session, sessionmaker

    from config.config import load_config

    config = load_config()
    engine = create_engine(config.database.url, future=True)
    return sessionmaker(bind=engine, expire_on_commit=False, class_=Session)


def cmd_seed(args: argparse.Namespace) -> int:
    from uuid import uuid4

    from sqlalchemy import func, select

    from application.services.card_factory import generate_cards, list_card_types
    from infrastructure.db.models import CardModel, CardTypeModel, UserModel

    SessionLocal = _make_session_factory()

    seed_users = [
        ("gandalf", uuid4()),
        ("saruman", uuid4()),
        ("radagast", uuid4()),
    ]

    with SessionLocal() as session:
        for username, user_id in seed_users:
            exists = session.scalar(
                select(UserModel).where(UserModel.username == username)
            )
            if exists:
                print(f"  skip  {username} (already exists)")
                continue
            session.add(UserModel(id=user_id, username=username))
            print(f"  add   {username}  id={user_id}")

        session.commit()

    with SessionLocal() as session:
        existing_card_type_ids = set(session.scalars(select(CardTypeModel.id)))
        for card_type in list_card_types():
            if card_type.id in existing_card_type_ids:
                continue
            session.add(
                CardTypeModel(
                    id=card_type.id,
                    action=card_type.action.value,
                    usage_pattern=card_type.usage_pattern.value,
                    if_permanent=card_type.if_permanent,
                    color=card_type.color,
                )
            )

        session.commit()

    with SessionLocal() as session:
        current_count = session.scalar(select(func.count()).select_from(CardModel)) or 0
        print(f"Current cards in db: {current_count}")
        target_count = args.cards
        if current_count >= target_count:
            print(f"  skip  card seed (already have {current_count} cards)")
        else:
            to_add = target_count - current_count
            cards = generate_cards(to_add)
            for card in cards:
                session.add(
                    CardModel(
                        id=card.id,
                        title=card.title,
                        creature=card.creature,
                        card_type_id=card.card_type_id,
                        power=card.power,
                        echo=card.echo,
                        cost=card.cost,
                        cool_points=card.cool_points,
                    )
                )
            session.commit()
            print(f"  add   {to_add} cards")

    print("Seed complete.")
    return 0


def cmd_truncate(args: argparse.Namespace) -> int:
    from sqlalchemy import MetaData, text

    SessionLocal = _make_session_factory()
    metadata = MetaData()

    with SessionLocal() as session:
        metadata.reflect(bind=session.get_bind())

        if args.table not in metadata.tables:
            available_tables = ", ".join(sorted(metadata.tables))
            raise ValueError(
                f"unknown table '{args.table}'. Available tables: {available_tables}"
            )

        cascade_sql = " CASCADE" if args.cascade else ""
        session.execute(text(f'TRUNCATE TABLE "{args.table}"{cascade_sql}'))
        session.commit()

    print(f"Table '{args.table}' truncated.")
    return 0


def cmd_truncate_all(args: argparse.Namespace) -> int:
    from sqlalchemy import MetaData, text

    SessionLocal = _make_session_factory()
    metadata = MetaData()

    with SessionLocal() as session:
        metadata.reflect(bind=session.get_bind())

        table_names = sorted(
            table_name
            for table_name in metadata.tables
            if args.include_alembic or table_name != "alembic_version"
        )
        if not table_names:
            print("No tables to truncate.")
            return 0

        joined_tables = ", ".join(f'"{table_name}"' for table_name in table_names)
        session.execute(text(f"TRUNCATE TABLE {joined_tables} CASCADE"))
        session.commit()

    print(f"Truncated tables: {', '.join(table_names)}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Database management")
    sub = parser.add_subparsers(dest="command", required=True)

    sub.add_parser("upgrade", help="Apply all migrations (alembic upgrade head)")
    sub.add_parser("current", help="Show current revision")
    p_seed = sub.add_parser(
        "seed",
        help="Insert demo users (gandalf, saruman, radagast) and default cards",
    )
    p_seed.add_argument(
        "--cards",
        type=int,
        default=100,
        help="Number of card records to populate in the database",
    )
    p_truncate = sub.add_parser("truncate", help="Delete all rows from a table")
    p_truncate.add_argument("table", help="Table name to truncate")
    p_truncate.add_argument(
        "--cascade",
        action="store_true",
        help="Also truncate dependent tables via CASCADE",
    )
    p_truncate_all = sub.add_parser(
        "truncate-all",
        help="Delete all rows from all tables in the current database",
    )
    p_truncate_all.add_argument(
        "--include-alembic",
        action="store_true",
        help="Also truncate alembic_version",
    )

    p_down = sub.add_parser("downgrade", help="Rollback migrations")
    p_down.add_argument(
        "revision",
        nargs="?",
        help="Target revision (default: -1 = one step back)",
    )

    p_rev = sub.add_parser("revision", help="Create new migration")
    p_rev.add_argument("message", help="Migration message")
    p_rev.add_argument(
        "--autogenerate",
        action="store_true",
        help="Autogenerate from SQLAlchemy models",
    )
    sub.add_parser("stamp", help="Mark DB schema as up-to-date (alembic stamp head)")

    args = parser.parse_args()
    handlers = {
        "upgrade": cmd_upgrade,
        "downgrade": cmd_downgrade,
        "revision": cmd_revision,
        "current": cmd_current,
        "stamp": cmd_stamp,
        "seed": cmd_seed,
        "truncate": cmd_truncate,
        "truncate-all": cmd_truncate_all,
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
