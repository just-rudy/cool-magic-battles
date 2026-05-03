from bootstrap.container import build_console_app
from infrastructure.logging.logger import get_logger, setup_logging


def main() -> None:
    setup_logging()
    logger = get_logger("main")
    logger.info("Application starting")

    app = build_console_app()
    logger.info("Console app built successfully")

    app.run()
    logger.info("Application stopped")


if __name__ == "__main__":
    main()
