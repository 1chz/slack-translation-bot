from typing import Callable, Any, Awaitable, Optional, Dict

from slack_bolt.async_app import AsyncApp

from .bot import TranslationBot, Message

SlackSayFunction = Callable[..., Awaitable[Any]]


class SlackTranslationClient:
    """Slack event handler and message dispatcher."""

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

            response: Optional[Dict[str, Any]] = await self.bot.translate(message)
            if response:
                await say(**response)
