"""Network connectivity validation service

Checks Telegram API connectivity during application bootstrap to ensure
the bot can communicate with Telegram servers before starting.
"""

from aiohttp import ClientSession, ClientTimeout

from src.config import settings
from src.utils.logger import logger


async def check_telegram_api_connection() -> None:
    """
    Validate Telegram API accessibility using bot token.

    Makes an HTTP request to Telegram Bot API getMe endpoint to verify:
    - Network connectivity to Telegram servers
    - Bot token validity
    - Telegram service availability

    Uses a short 3-second timeout to fail fast if connection issues occur.
    Failures are logged but don't halt application startup (graceful degradation).

    API endpoint: https://api.telegram.org/bot{token}/getMe

    Side effects:
        - Logs success if API is accessible and responds with ok=true
        - Logs warning if API responds but with ok=false
        - Logs error if request fails or API returns error status

    Notes:
        - Used during bootstrap to catch configuration issues early
        - Non-blocking - failures don't prevent application startup
        - Helps identify invalid bot tokens or network issues

    Raises:
        No exceptions are raised - all errors are logged
    """

    url = f"https://api.telegram.org/bot{settings.BOT_TOKEN}/getMe"
    timeout = ClientTimeout(total=3)

    # ToDo make better error catch  # pylint: disable=fixme
    try:
        async with ClientSession(timeout=timeout) as session:
            async with session.get(url) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("ok"):
                        logger.success("Telegram API is accessible")
                    else:
                        logger.warning("Telegram API responded, but returned not ok")
                else:
                    logger.error("Telegram API error > %s", response.status)
    except Exception as e:
        logger.error("Telegram API check failed: %s", e)
