from typing import Optional, AsyncContextManager, Dict

import aiohttp
from pydantic import BaseModel

from .config import LLMConfig


class TranslationResponse(BaseModel):
    """
    Slack Block Kit formatted translation response.
    Ref. https://api.slack.com/reference/surfaces/formatting
    """

    blocks: list[Dict]


class Translator(AsyncContextManager["Translator"]):
    """Handles communication with the LLM translation service.

    Responsible for sending translation requests to the LLM service and
    processing the responses in Slack Block Kit format.
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config: LLMConfig = config
        self.session: Optional[aiohttp.ClientSession] = None
        self.translation_prompt = """
        You are a translation assistant. Please translate the given text according to these rules:
        
        1. If the input is in Korean:
           - Translate to English
           - Translate to Thai
        
        2. If the input is in Thai:
           - Translate to English 
           - Translate to Korean
        
        3. If the input is in English:
           - Translate to Korean
           - Translate to Thai
        
        Translation Guidelines:
        - Maintain the original meaning and nuance
        - Keep proper nouns and technical terms accurate
        - Provide natural and fluent translations
        - Use country flag emojis (🇰🇷 🇺🇸 🇹🇭) before each translation
        - Show original text in a separate block
        - Use Slack's Block Kit JSON format
        
        Output Format:
        {
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "Original Text Block"
                    }
                },
                {
                    "type": "divider"
                },
                {
                    "type": "section", 
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "Translation 1"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "Translation 2"
                        }
                    ]
                }
            ]
        }
        
        Input Message: {text}
        """  # noqa: W291, W293, E501

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

    async def translate(self, text: str) -> TranslationResponse:
        """Translates text using the LLM service.

        Args:
            text: The text to translate

        Returns:
            TranslationResponse containing Slack Block Kit formatted translations

        Raises:
            RuntimeError: If called outside of context manager
            HTTPError: If the LLM service request fails
        """
        if not self.session:
            raise RuntimeError("Session not initialized. Use async with context.")

        prompt = self.translation_prompt.format(text=text)

        async with self.session.post(
            str(self.config.api_url), json={"prompt": prompt}
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return TranslationResponse.model_validate(result)
