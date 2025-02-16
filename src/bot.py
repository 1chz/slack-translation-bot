from typing import Optional, Dict, List, Set
from dataclasses import dataclass
from .translator import Translator
from .config import SupportedLanguage


@dataclass
class Message:
    """Data container for Slack messages.

    Represents a normalized Slack message structure, containing only the
    fields relevant for translation processing. This class simplifies
    message handling by providing a consistent interface regardless of
    the original Slack event structure.

    Attributes:
        text: The message content to be translated
        channel: The Slack channel ID where the message was sent
        user: The Slack user ID who sent the message
        ts: Message timestamp (used as unique identifier)
        thread_ts: Parent thread timestamp if message is in a thread
    """

    text: str
    channel: str
    user: str
    ts: str
    thread_ts: Optional[str] = None


class TranslationBot:
    """Core translation bot logic handler.

    This class is responsible for implementing the bot's translation logic,
    including language detection, translation direction decisions, and
    message formatting. It acts as the coordination layer between Slack
    events and the translation service.

    Key responsibilities:
    - Determines which messages should be translated
    - Manages translation direction based on detected language
    - Formats translation results for Slack display
    - Handles bot commands and responses

    Attributes:
        translator: Translation service client
        supported_languages: Mapping of language codes to their names
        translation_targets: Mapping of source languages to their target languages
    """

    def __init__(self, translator: Translator) -> None:
        self.translator: Translator = translator
        self.supported_languages: Dict[SupportedLanguage, str] = {
            "ko": "Korean",
            "en": "English",
            "th": "Thai",
        }
        self.translation_emoji: str = "🌐"

        self.translation_targets: Dict[SupportedLanguage, Set[SupportedLanguage]] = {
            "ko": {"en", "th"},
            "en": {"ko", "th"},
            "th": {"ko", "en"},
        }

    async def process_message(self, message: Message) -> Optional[List[str]]:
        if self._should_skip_translation(message.text):
            return None

        try:
            source_lang: SupportedLanguage = await self._detect_language(message.text)

            # If it is a language that does not supported
            if source_lang not in self.translation_targets:
                return None

            # Translated into target languages in the source language
            translations: List[str] = []
            async with self.translator as t:
                for target_lang in self.translation_targets[source_lang]:
                    translated_text = await t.translate(
                        text=message.text,
                        source_lang=source_lang,
                        target_lang=target_lang,
                    )
                    translations.append(
                        self._format_translation(
                            translated_text, source_lang, target_lang
                        )
                    )
            return translations

        except Exception as e:
            print(f"Translation error: {e}")
            return None

    def _should_skip_translation(self, text: str) -> bool:
        """Determines if a message should be skipped for translation."""
        if text.startswith(f"{self.translation_emoji} "):
            return True

        if not text or text.startswith("/"):
            return True

        if text.startswith(("http://", "https://")):
            return True

        return False

    async def _detect_language(self, text: str) -> SupportedLanguage:
        """Detects the language of the input text."""
        async with self.translator as t:
            return await t.detect_language(text)

    def _format_translation(
        self,
        translated_text: str,
        source_lang: SupportedLanguage,
        target_lang: SupportedLanguage,
    ) -> str:
        """Formats the translation result for display in Slack."""
        return (
            f"{self.translation_emoji} [{source_lang} → {target_lang}] "
            f"{translated_text}"
        )

    def _get_supported_languages(self) -> str:
        """Returns a formatted list of supported languages."""
        return """
            Supported languages and translation paths:
            • Korean → English, Thai
            • English → Korean, Thai
            • Thai → Korean, English
            """
