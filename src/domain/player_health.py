"""Правила очков здоровья (ОЗ) игрока."""

DEFAULT_PLAYER_HEALTH = 20
MAX_PLAYER_HEALTH = 25


def apply_heal(current_health: int, heal_power: int) -> int:
    return min(current_health + heal_power, MAX_PLAYER_HEALTH)


def health_after_death() -> int:
    """ОЗ после смерти и возрождения."""
    return DEFAULT_PLAYER_HEALTH
