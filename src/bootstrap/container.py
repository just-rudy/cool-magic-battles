from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from application.controllers.card_controller import CardController
from application.controllers.game_controller import GameController
from application.controllers.user_controller import UserController
from application.services import CardLogic, DeckService, GameLogic, GameStateManager
from config.config import load_config
from infrastructure.db.repositories.sqlalchemy_card_repository import (
    SqlAlchemyCardRepository,
)
from infrastructure.db.repositories.sqlalchemy_game_repository import (
    SqlAlchemyGameRepository,
)
from infrastructure.db.repositories.sqlalchemy_user_repository import (
    SqlAlchemyUserRepository,
)
from infrastructure.db.utils import create_tables
from infrastructure.ui.console.console_app import ConsoleApp


def build_console_app() -> ConsoleApp:
    config = load_config()
    engine = create_engine(config.database.url, future=True)
    create_tables(engine)

    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    game_repo = SqlAlchemyGameRepository(session)
    user_repo = SqlAlchemyUserRepository(session)
    card_repo = SqlAlchemyCardRepository(session)

    game_logic = GameLogic(
        game_repository=game_repo,
        user_repository=user_repo,
        card_logic=CardLogic(),
        deck_service=DeckService(),
        game_state_manager=GameStateManager(),
    )

    game_controller = GameController(
        game_logic,
        game_repo,
        card_repo,
        default_market_size=config.game.default_market_size,
    )
    user_controller = UserController(user_repo)
    card_controller = CardController(card_repo)

    return ConsoleApp(
        game_controller=game_controller,
        user_controller=user_controller,
        card_controller=card_controller,
    )
