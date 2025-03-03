import asyncio
import json
from typing import Callable, Any, Awaitable

from slack_bolt.adapter.socket_mode.async_handler import AsyncSocketModeHandler
from slack_bolt.app.async_app import AsyncApp
from slack_sdk.web.async_client import AsyncWebClient

from src.logger import setup_logger
from .bot import TranslationBot
from .config import APP_CONFIG
from .slack_models import Message
from .translator import Translator

SlackSayFunction = Callable[..., Awaitable[Any]]

logger = setup_logger(__name__)

app = AsyncApp(
    token=APP_CONFIG.slack_config.bot_token,
    signing_secret=APP_CONFIG.slack_config.signing_secret,
)

translator: Translator = None  # type: ignore
bot: TranslationBot = None  # type: ignore


@app.event("message")
async def handle_message(
    event: dict, say: SlackSayFunction, client: AsyncWebClient
) -> None:
    logger.debug(f"Received message event: {event}")

    if _is_bot_message(event):
        return

    message = Message.from_event(event)
    if not message:
        return

    if _is_message_update(event):
        await _handle_message_update(message, client)
        return

    if await _translation_exists(message, client):
        return

    await _send_translation(message, say)


def _is_bot_message(event: dict) -> bool:
    if event.get("subtype") == "bot_message":
        logger.debug("Ignoring bot message")
        return True
    return False


def _is_message_update(event: dict) -> bool:
    return event.get("subtype") == "message_changed"


async def _translation_exists(message: Message, client: AsyncWebClient) -> bool:
    try:
        thread_response = await client.conversations_replies(
            ts=message.ts,
            channel=message.channel,
        )

        if thread_response.get("messages"):
            bot_replies = [
                msg
                for msg in thread_response["messages"]
                if msg.get("bot_id") and msg["ts"] != message.ts
            ]
            if bot_replies:
                logger.debug("Translation already exists, skipping...")
                return True
    except Exception as e:
        logger.error(f"Error checking thread replies: {e}")

    return False


async def _send_translation(message: Message, say: SlackSayFunction) -> None:
    response = await bot.translate(message)
    if response:
        await say(
            thread_ts=response.thread_ts,
            text=response.text,
            blocks=response.blocks,
        )


async def _handle_message_update(message: Message, client: AsyncWebClient) -> None:
    try:
        thread_response = await client.conversations_replies(
            channel=message.channel, ts=message.thread_ts
        )

        messages: list[dict[str, Any]] = thread_response.get("messages", [])
        bot_replies: list[dict[str, Any]] = [
            msg for msg in messages if msg.get("bot_id")
        ]

        if not bot_replies:
            logger.debug("No translation found for updated message")
            return

        new_translation = await bot.translate(message)
        if not new_translation:
            return

        for reply in bot_replies:
            try:
                await client.chat_update(
                    channel=message.channel,
                    ts=reply["ts"],
                    text=new_translation.text,
                    blocks=json.dumps(new_translation.blocks),
                )
                logger.debug(f"Updated translation for message {message.ts}")
            except Exception as e:
                logger.error(f"Error updating translation: {e}")

    except Exception as e:
        logger.error(f"Error handling message update: {e}")


async def _initialize_components():
    """Initialize translator and bot components."""
    global translator, bot
    translator = Translator(APP_CONFIG.llm_config)
    bot = TranslationBot(translator)


async def start_async_handler():
    try:
        await _initialize_components()

        handler = AsyncSocketModeHandler(app, APP_CONFIG.slack_config.app_token)
        await handler.connect_async()
        logger.info("⚡️ Bolt app is running!")

        try:
            await asyncio.Future()  # run forever
        finally:
            if translator:
                await translator.close()
            await handler.disconnect_async()

    except Exception as e:
        logger.error(f"Error in socket mode handler: {e}", exc_info=True)
        raise
