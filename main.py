import asyncio
import os
import signal
from typing import NoReturn

from dotenv import load_dotenv
from pydantic import HttpUrl
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.async_app import AsyncApp

from src.bot import TranslationBot
from src.config import AppConfig, SlackConfig, LLMConfig
from src.logger import setup_logger
from src.slack_client import SlackTranslationClient
from src.translator import Translator

logger = setup_logger(__name__)


class EnvironmentError(Exception):
    """Raised when required environment variables are missing."""

    pass


def validate_environment() -> None:
    """
    Validates that all required environment variables are set.

    Raises:
        EnvironmentError: If any required environment variable is missing.
    """
    required_vars = {
        "SLACK_BOT_TOKEN": os.getenv("SLACK_BOT_TOKEN"),
        "SLACK_SIGNING_SECRET": os.getenv("SLACK_SIGNING_SECRET"),
        "LLM_API_URL": os.getenv("LLM_API_URL"),
        "LLM_API_TOKEN": os.getenv("LLM_API_TOKEN"),
    }

    missing_vars = [key for key, value in required_vars.items() if not value]

    if missing_vars:
        error_msg = (
            f"Missing required environment variables: {', '.join(missing_vars)}\n"
            "Please check your .env file and ensure all required variables are set."
        )
        logger.error(error_msg)
        raise EnvironmentError(error_msg)


def handle_startup_error(error: Exception) -> NoReturn:
    """
    Handles startup errors by logging them and exiting the program.

    Args:
        error: The exception that occurred during startup.
    """
    logger.error(f"Failed to start the bot: {str(error)}")
    logger.error("Shutting down due to startup error.")
    exit(1)


async def main() -> None:
    """Main entry point for the Slack Translation Bot."""
    logger.info("Starting application...")

    try:
        logger.info("Loading environment variables...")
        load_dotenv()
        validate_environment()

        logger.info("Initializing configuration...")
        config = AppConfig(
            slack=SlackConfig(
                bot_token=os.getenv("SLACK_BOT_TOKEN", ""),
                signing_secret=os.getenv("SLACK_SIGNING_SECRET", ""),
            ),
            llm=LLMConfig(
                api_url=(HttpUrl(os.getenv("LLM_API_URL", ""))),
                api_token=os.getenv("LLM_API_TOKEN", ""),
            ),
        )

        logger.info("Initializing Slack app...")
        app = AsyncApp(
            token=config.slack.bot_token,
            signing_secret=config.slack.signing_secret,
        )

        # Initialize components
        translator = Translator(config.llm)
        bot = TranslationBot(translator)
        client = SlackTranslationClient(app, bot)  # noqa: F841

        # Set up shutdown signal handling
        stop_event = asyncio.Event()

        async def signal_handler() -> None:
            logger.info("Received shutdown signal. Shutting down gracefully...")
            stop_event.set()

        # Register signal handlers for graceful shutdown
        for sig in (signal.SIGINT, signal.SIGTERM):
            asyncio.get_event_loop().add_signal_handler(
                sig, lambda: asyncio.create_task(signal_handler())
            )

        # Initialize Socket Mode handler
        handler = AsyncSocketModeHandler(
            app=app,
            app_token=os.getenv("SLACK_APP_TOKEN", ""),
        )

        try:
            # Start the bot
            await handler.connect_async()
            logger.info("Translation Bot is now running!")

            # Wait for shutdown signal
            await stop_event.wait()
        finally:
            # Clean up resources
            await handler.disconnect_async()
            logger.info("Translation Bot has been successfully shut down")

    except EnvironmentError as e:
        handle_startup_error(e)
    except Exception as e:
        handle_startup_error(e)


if __name__ == "__main__":
    asyncio.run(main())
