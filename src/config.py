from pydantic import BaseModel, Field, HttpUrl


class SlackConfig(BaseModel):
    """Slack bot configuration settings.

    Contains the necessary credentials for Slack API authentication.
    """

    bot_token: str = Field(..., min_length=1)
    signing_secret: str = Field(..., min_length=1)


class LLMConfig(BaseModel):
    """LLM service configuration settings.

    Contains the configuration for the LLM translation service.
    """

    api_url: HttpUrl
    api_token: str = Field(..., min_length=1)


class AppConfig(BaseModel):
    """Application configuration container.

    Validates and provides access to all application configuration settings.
    """

    slack: SlackConfig
    llm: LLMConfig
