from typing import Optional, Dict, Any
from dataclasses import dataclass
from .translator import Translator
from src.logger import setup_logger

logger = setup_logger(__name__)


@dataclass
class Message:
    """Data container for Slack messages."""

    text: str
    channel: str
    user: str
    ts: str
    thread_ts: Optional[str] = None


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

    async def translate(self, message: Message) -> Optional[Dict[str, Any]]:
        """Translate a message and returns translations if appropriate."""
        if self._should_skip_translation(message.text):
            return None

        try:
            async with self.translator as t:
                response = await t.translate(message.text)
                return {"blocks": response.blocks}
        except Exception as e:
            logger.error(f"Translation error: {e}")
            return None
