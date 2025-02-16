from typing import Literal
from pydantic import BaseModel, Field, HttpUrl


class SlackConfig(BaseModel):
    """Slack bot configuration settings.

    Handles validation and storage of all Slack-related credentials and settings
    required for the bot to connect to and interact with Slack.

    Attributes:
        signing_secret: Slack signing secret for request verification
        bot_token: Bot user OAuth token for Slack API operations
        app_token: App-level token for Socket Mode connection
    """

    signing_secret: str = Field(..., min_length=1)
    bot_token: str = Field(..., min_length=1)
    app_token: str = Field(..., min_length=1)


class TranslationConfig(BaseModel):
    """Translation service configuration settings.

    Contains and validates the configuration needed to connect to the external
    translation service.

    Attributes:
        api_url: Translation service API endpoint URL
        api_token: Authentication token for the translation service
    """

    api_url: HttpUrl
    api_token: str = Field(..., min_length=1)


class AppConfig(BaseModel):
    """Application configuration container.

    This class is responsible for validating and providing access to all configuration
    settings needed by the application. It uses Pydantic for validation to ensure
    all required settings are properly set at startup.

    Attributes:
        slack: Slack-specific configuration settings
        translation: Translation service configuration settings
    """

    slack: SlackConfig
    translation: TranslationConfig


SupportedLanguage = Literal["ko", "en", "th"]
"""Type hint for supported language codes.

This type ensures type safety by restricting language codes to only supported values.
It helps prevent runtime errors by catching invalid language codes during type checking.

Supported codes:
    - "ko": Korean
    - "en": English
    - "th": Thai

Example:
    # Only allows "ko", "en", "th"
    def translate(text: str, lang: SupportedLanguage) -> str:
        ...

Note:
    Using this type instead of `str` provides:
    - Type safety: Catches invalid language codes at compile time
    - Auto-completion in IDEs
    - Clear documentation of supported languages
    - Better maintainability when adding/removing supported languages
"""
