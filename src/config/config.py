import os
from dataclasses import dataclass
from pathlib import Path

DEFAULT_CONFIG_PATH = Path(__file__).with_name("config.yaml")
DEFAULT_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


@dataclass(frozen=True)
class DatabaseConfig:
    url: str


@dataclass(frozen=True)
class GameConfig:
    default_hand_size: int = 5
    default_market_size: int = 5
    default_base_health: int = 20


@dataclass(frozen=True)
class LoggingConfig:
    file: str = "logs/app.log"


@dataclass(frozen=True)
class Config:
    database: DatabaseConfig
    game: GameConfig
    logging: LoggingConfig


def _load_env_file(env_path: Path = DEFAULT_ENV_PATH) -> None:
    if not env_path.exists():
        return

    for line in env_path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue

        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def _clean_yaml_value(value: str) -> str:
    value = value.strip()
    return value.strip("\"'")


def _load_yaml_config(
    config_path: Path = DEFAULT_CONFIG_PATH,
) -> dict[str, dict[str, str]]:
    if not config_path.exists():
        return {}

    data: dict[str, dict[str, str]] = {}
    section: str | None = None

    for line in config_path.read_text().splitlines():
        if not line.strip() or line.lstrip().startswith("#"):
            continue

        indent = len(line) - len(line.lstrip())
        stripped = line.strip()

        if indent == 0 and stripped.endswith(":"):
            section = stripped[:-1]
            data.setdefault(section, {})
            continue

        if section is None or ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        data[section][key.strip()] = _clean_yaml_value(value)

    return data


def load_config(config_path: Path = DEFAULT_CONFIG_PATH) -> Config:
    _load_env_file()
    file_config = _load_yaml_config(config_path)
    database_config = file_config.get("database", {})
    game_config = file_config.get("game", {})
    logging_config = file_config.get("logging", {})
    database_url = os.getenv("DATABASE_URL", database_config.get("url"))

    if database_url is None:
        raise ValueError("database.url must be set in config.yaml or DATABASE_URL")

    return Config(
        database=DatabaseConfig(url=database_url),
        game=GameConfig(
            default_hand_size=int(
                os.getenv(
                    "DEFAULT_HAND_SIZE",
                    game_config.get("default_hand_size", GameConfig.default_hand_size),
                )
            ),
            default_market_size=int(
                os.getenv(
                    "DEFAULT_MARKET_SIZE",
                    game_config.get(
                        "default_market_size", GameConfig.default_market_size
                    ),
                )
            ),
            default_base_health=int(
                os.getenv(
                    "DEFAULT_BASE_HEALTH",
                    game_config.get(
                        "default_base_health", GameConfig.default_base_health
                    ),
                )
            ),
        ),
        logging=LoggingConfig(
            file=os.getenv("LOG_FILE", logging_config.get("file", LoggingConfig.file))
        ),
    )
