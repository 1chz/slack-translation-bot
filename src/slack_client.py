from typing import Optional, Callable, Any, Awaitable, List
from slack_bolt.async_app import AsyncApp
from .bot import TranslationBot, Message


SlackSayFunction = Callable[..., Awaitable[Any]]


class SlackTranslationClient:
    """Slack event handler and message dispatcher.

    This class is responsible for integrating with Slack's event system and
    coordinating message processing. It receives Slack events, processes them
    through the translation bot, and sends responses back to Slack.

    Key responsibilities:
    - Registers and handles Slack event callbacks
    - Filters and processes incoming messages
    - Manages message threading and responses
    - Coordinates between Slack events and bot logic

    The client maintains the connection to Slack and ensures proper message
    handling and response delivery.

    Attributes:
        app: Slack Bolt application instance
        bot: Translation bot instance for message processing
    """

    __slots__ = ["app", "bot"]

    def __init__(self, app: AsyncApp, bot: TranslationBot) -> None:
        self.app: AsyncApp = app
        self.bot: TranslationBot = bot
        self._register_handlers()

    def _register_handlers(self) -> None:
        @self.app.event("message")
        async def handle_message(event: dict, say: SlackSayFunction) -> None:
            if event.get("subtype") == "bot_message":
                return

            message = Message(
                text=event.get("text", ""),
                channel=event.get("channel", ""),
                user=event.get("user", ""),
                ts=event.get("ts", ""),
                thread_ts=event.get("thread_ts"),
            )

            translations: Optional[List[str]] = await self.bot.process_message(message)
            if translations:
                for translation in translations:
                    await say(
                        text=translation,
                        thread_ts=message.thread_ts or message.ts,
                    )
