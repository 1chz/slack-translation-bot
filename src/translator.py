from typing import Optional, AsyncContextManager
import aiohttp
from pydantic import BaseModel

from .config import TranslationConfig, SupportedLanguage


class TranslationResponse(BaseModel):
    """
    Represents a translation response from the service.
    """

    translated_text: str
    detected_language: SupportedLanguage


class Translator(AsyncContextManager["Translator"]):
    """Handles communication with the translation service.

    This class is responsible for managing the connection to the translation service
    and performing translation operations. It implements the async context manager
    protocol for proper resource management.

    The translator maintains a single aiohttp session for efficient API communication
    and should be used within an async context manager:

    Example:
        async with Translator(config) as translator:
            result = await translator.translate("Hello", target_lang="ko")

    Attributes:
        config: Configuration for connecting to the translation service
        session: Managed aiohttp client session for API requests
    """

    def __init__(self, config: TranslationConfig) -> None:
        self.config: TranslationConfig = config
        self.session: Optional[aiohttp.ClientSession] = None

    async def __aenter__(self) -> "Translator":
        self.session = aiohttp.ClientSession(
            headers={"Authorization": f"Bearer {self.config.api_token}"}
        )
        return self

    async def __aexit__(
        self,
        exc_type: Optional[type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[object],
    ) -> None:
        if self.session:
            await self.session.close()

    async def translate(
        self,
        text: str,
        source_lang: Optional[SupportedLanguage] = None,
        target_lang: SupportedLanguage = "en",
    ) -> str:
        """Translates text to the target language.

        Args:
            text: The text to translate
            source_lang: Source language code (auto-detected if None)
            target_lang: Target language code for translation

        Returns:
            The translated text

        Raises:
            RuntimeError: If called outside of context manager
            HTTPError: If the translation service request fails
        """

        if not self.session:
            raise RuntimeError("Session not initialized. Use async with context.")

        async with self.session.post(
            str(self.config.api_url),
            json={
                "text": text,
                "source_language": source_lang,
                "target_language": target_lang,
            },
        ) as response:
            response.raise_for_status()
            result = TranslationResponse.model_validate(await response.json())
            return result.translated_text

    async def detect_language(self, text: str) -> SupportedLanguage:
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with context.")

        async with self.session.post(
            f"{self.config.api_url}/detect",
            json={"text": text},
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return result["detected_language"]
