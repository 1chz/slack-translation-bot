import asyncio

from src.logger import setup_logger
from src.slack_handler import start_async_handler

logger = setup_logger(__name__)


async def main():
    try:
        await start_async_handler()
    except Exception as e:
        logger.error(f"Application error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())
