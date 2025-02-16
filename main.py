import asyncio
import signal
from pathlib import Path
import yaml
from dotenv import load_dotenv
from slack_bolt.async_app import AsyncApp
from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler

from src.config import AppConfig
from src.translator import Translator
from src.bot import TranslationBot
from src.slack_client import SlackTranslationClient


async def main() -> None:
    load_dotenv()

    # Load and validate configuration
    config_path = Path("config/config.yaml")
    with config_path.open() as cf:
        config_dict = yaml.safe_load(cf)

    config: AppConfig = AppConfig.model_validate(config_dict)

    app = AsyncApp(
        token=config.slack.bot_token,
        signing_secret=config.slack.signing_secret,
    )

    translator = Translator(config.translation)
    bot = TranslationBot(translator)
    client = SlackTranslationClient(app, bot)  # noqa: F841

    # Shutdown signal handling event
    stop_event = asyncio.Event()

    async def signal_handler() -> None:
        print("\n⚡️ Shutting down gracefully...")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        asyncio.get_event_loop().add_signal_handler(
            sig, lambda: asyncio.create_task(signal_handler())
        )

    handler = AsyncSocketModeHandler(app, config.slack.app_token)

    try:
        await handler.connect_async()
        print("⚡️ Translation Bot is running!")

        await stop_event.wait()
    finally:
        await handler.disconnect_async()
        print("⚡️ Bot has been shut down")


if __name__ == "__main__":
    asyncio.run(main())
