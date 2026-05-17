from dataclasses import dataclass


@dataclass
class ParsedInstruction:
    task: str
    nickname: str | None = None
    user_id: str | None = None
    player_id: str | None = None
    game_id: str | None = None
    card_ref: str | None = None


COMMAND_FIELDS: dict[str, list[str]] = {
    "reg": ["nickname"],
    "login": ["user_id", "game_id"],
    "as": ["user_id", "game_id"],
    "run": ["game_id"],
    "join": ["user_id", "game_id"],
    "game": ["game_id"],
    "play": ["card_ref", "game_id"],
    "buy": ["card_ref", "game_id"],
    "end": ["game_id"],
    "hand": ["player_id"],
    "draw": ["player_id"],
    "discard": ["player_id"],
    "market": ["game_id"],
    "players": ["game_id"],
    "gen_decks": ["game_id"],
}


def parse_instruction(raw: str) -> ParsedInstruction:
    raw_parts = list(raw.strip().split())

    if not raw_parts:
        raise ValueError("err: empty instruction")

    instr = ParsedInstruction(task=raw_parts[0])
    fields = COMMAND_FIELDS.get(raw_parts[0], [])

    for field, value in zip(fields, raw_parts[1:], strict=False):
        setattr(instr, field, value)

    return instr
