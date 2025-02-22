import os

from typing import Optional

from dotenv import load_dotenv
from pydantic import BaseModel, Field, HttpUrl

from src.logger import setup_logger

logger = setup_logger(__name__)
load_dotenv()


class EnvironmentVariableError(Exception):
    """Raised when required environment variables are missing."""

    pass


class SlackConfig(BaseModel):
    """Slack bot configuration settings.

    Contains the necessary credentials for Slack API authentication.
    """

    app_token: str = Field(..., min_length=1)
    bot_token: str = Field(..., min_length=1)
    signing_secret: str = Field(..., min_length=1)


class LLMConfig(BaseModel):
    """LLM service configuration settings.

    Contains the configuration for the LLM translation service.
    """

    api_url: HttpUrl
    api_token: Optional[str]


class AppConfig(BaseModel):
    """Application configuration container.

    Validates and provides access to all application configuration settings.
    """

    slack_config: SlackConfig
    llm_config: LLMConfig


def get_env_or_raise(key: str) -> str:
    """
    Get an environment variable or raise an exception if it's missing or empty.

    Args:
        key: The name of the environment variable

    Returns:
        The value of the environment variable

    Raises:
        EnvironmentVariableError: If the environment variable is missing or empty
    """
    value: Optional[str] = os.getenv(key)

    if not value:
        error_msg = f"Environment variable '{key}' is missing or empty"
        logger.error(error_msg)
        raise EnvironmentVariableError(error_msg)

    return value


logger.info(">>> Loading settings...")

SLACK_APP_TOKEN = get_env_or_raise("SLACK_APP_TOKEN")
SLACK_BOT_TOKEN = get_env_or_raise("SLACK_BOT_TOKEN")
SLACK_SIGNING_SECRET = get_env_or_raise("SLACK_SIGNING_SECRET")
LLM_API_URL = HttpUrl(get_env_or_raise("LLM_API_URL"))
LLM_API_TOKEN = os.getenv("LLM_API_TOKEN")

SLACK_CONFIG = SlackConfig(
    app_token=SLACK_APP_TOKEN,
    bot_token=SLACK_BOT_TOKEN,
    signing_secret=SLACK_SIGNING_SECRET,
)
LLM_CONFIG = LLMConfig(api_url=LLM_API_URL, api_token=LLM_API_TOKEN)
APP_CONFIG = AppConfig(slack_config=SLACK_CONFIG, llm_config=LLM_CONFIG)

logger.info(">>> Settings loaded.")
