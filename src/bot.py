import json
from dataclasses import dataclass
from typing import Optional, Dict, Any

from pydantic import BaseModel

from src.logger import setup_logger
from .translator import Translator

logger = setup_logger(__name__)


class MessageResponse(BaseModel):
    """
    Slack Block Kit formatted translation response.
    Ref. https://api.slack.com/reference/surfaces/formatting
    """

    thread_ts: str
    text: str
    blocks: list[Dict[str, Any]]


@dataclass
class Message:
    """Data container for Slack messages."""

    text: str
    channel: str
    user: str
    ts: str
    thread_ts: str

    @classmethod
    def from_event(cls, event: Dict[str, Any]) -> Optional["Message"]:
        """Create a Message instance from a Slack event dictionary."""
        if event.get("subtype") == "bot_message":
            return None

        if event.get("subtype") == "message_changed":
            message_data = event.get("message", {})
            return cls(
                text=message_data.get("text", ""),
                channel=event.get("channel", ""),
                user=message_data.get("user", ""),
                ts=message_data.get("ts", ""),
                thread_ts=message_data.get("thread_ts"),
            )

        return cls(
            **{
                k: event.get(k, "")
                for k in ["text", "channel", "user", "ts", "thread_ts"]
            }
        )


class TranslationBot:
    """Core translation bot logic handler.

    Coordinates between Slack events and the LLM translation service.
    """

    def __init__(self, translator: Translator) -> None:
        self.translator: Translator = translator

    def _should_skip_translation(self, text: str) -> bool:
        """Determines if a message should be skipped for translation."""

        if not text or text.startswith("/"):
            return True

        if text.startswith(("http://", "https://")):
            return True

        return False

    async def translate(self, message: Message) -> Optional[MessageResponse]:
        """Translate a message and returns translations if appropriate."""
        if self._should_skip_translation(message.text):
            return None

        try:
            translated = await self.translator.translate(message.text)
            return MessageResponse(
                thread_ts=message.ts,
                text=translated.response,
                blocks=json.loads(translated.response)["blocks"],
            )
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
