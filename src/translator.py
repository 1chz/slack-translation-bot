from string import Template

import aiohttp
from pydantic import BaseModel

from .config import LLMConfig
from .logger import setup_logger

logger = setup_logger(__name__)


class TranslationResponse(BaseModel):
    """
    Slack Block Kit formatted translation response.
    Ref. https://api.slack.com/reference/surfaces/formatting
    """

    response: str


class Translator:
    """Handles communication with the LLM translation service."""

    def __init__(self, config: LLMConfig) -> None:
        self.config: LLMConfig = config
        logger.debug("Creating HTTP session...")

        headers = {}
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
            logger.debug("Added Authorization header to HTTP session")
        self.session: aiohttp.ClientSession = aiohttp.ClientSession(headers=headers)
        logger.debug("HTTP session created successfully")

        self.translation_prompt = Template(
            """
                You are a translation assistant.
                You must strictly follow the rules below. 
                In particular, you must exclude any unnecessary responses, and the response format must be in JSON format. 
                Please translate the given text according to these rules:

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
                - Original text goes on top, other languages below
                - Use Slack's Block Kit JSON format
                
                Original Text: 
                $text

                Response Format:
                {
                    "blocks": [
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "{{ Original Text }}"
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
                                    "text": "{{ Translated Text 1 }}"
                                },
                                {
                                    "type": "mrkdwn",
                                    "text": "{{ Translated Text 2 }}"
                                }
                            ]
                        }
                    ]
                }
                """  # noqa: W291, W293, E501
        )

    async def close(self) -> None:
        """Close the HTTP session."""
        if self.session:
            logger.debug("Closing HTTP session...")
            await self.session.close()
            logger.debug("HTTP session closed successfully")

    async def translate(self, text: str) -> TranslationResponse:
        """Translates text using the LLM service.

        Args:
            text: The text to translate

        Returns:
            TranslationResponse containing Slack Block Kit formatted translations

        Raises:
            HTTPError: If the LLM service request fails
        """
        prompt = self.translation_prompt.substitute(text=text)

        async with self.session.post(
            str(self.config.api_url),
            json={"model": "llama2", "prompt": prompt, "stream": False},
        ) as response:
            response.raise_for_status()
            result = await response.json()
            return TranslationResponse.model_validate(result)
