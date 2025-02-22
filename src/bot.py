import json
from typing import Optional

from src.logger import setup_logger
from .slack_models import Message, MessageResponse
from .translator import Translator

logger = setup_logger(__name__)


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
