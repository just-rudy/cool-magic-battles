from uuid import UUID
from rich.console import Console

from infrastructure.ui.console.formatters import format_warn


def read_instruction(cnsl: Console | None = None) -> str:
    while True:
        raw = input(": ").strip()
        if raw:
            return raw
        if cnsl is not None:
            cnsl.print(format_warn("empty instruction"))


def read_word(prompt: str, cnsl: Console) -> str:
    while True:
        raw = input(prompt).strip()
        if raw:
            return raw
        cnsl.print(format_warn(f"empty {prompt[:-2].strip()}"))


def read_uuid(prompt: str, cnsl: Console) -> UUID:
    while True:
        raw = input(prompt).strip()
        try:
            return UUID(raw)
        except ValueError:
            cnsl.print(format_warn(f"invalid {prompt[:-2].strip()}"))


def read_word_optional(prompt: str, cnsl: Console) -> str | None:
    raw = input(prompt).strip()
    if not raw:
        return None
    return raw


def read_uuid_optional(prompt: str, cnsl: Console) -> UUID | None:
    raw = input(prompt).strip()
    if not raw:
        return None
    try:
        return UUID(raw)
    except ValueError:
        raise ValueError(f"invalid {prompt[:-2].strip()}")
