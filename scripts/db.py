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


def cmd_seed(args: argparse.Namespace) -> int:
    sys.path.insert(0, str(SRC))

    from uuid import uuid4

    from sqlalchemy import create_engine, func, select
    from sqlalchemy.orm import Session, sessionmaker

    from application.services.card_factory import generate_cards
    from config.config import load_config
    from infrastructure.db.models import CardModel, UserModel

    config = load_config()
    engine = create_engine(config.database.url, future=True)
    SessionLocal = sessionmaker(bind=engine, expire_on_commit=False, class_=Session)

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
    }
    return handlers[args.command](args)


if __name__ == "__main__":
    raise SystemExit(main())
