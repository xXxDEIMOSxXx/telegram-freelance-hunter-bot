"""Logger for printing messages in console"""

import logging
import sys

from colorama import Fore, Style, init

init(autoreset=True)  # autoreset string color


class ColoredFormatter(logging.Formatter):
    """Formatter with colored log messages"""

    LEVEL_COLORS = {  # color palette
        logging.DEBUG: Fore.LIGHTCYAN_EX,
        logging.INFO: Fore.LIGHTGREEN_EX,
        logging.WARNING: Fore.LIGHTYELLOW_EX,
        logging.ERROR: Fore.LIGHTRED_EX,
        logging.CRITICAL: Fore.LIGHTMAGENTA_EX,
    }

    def format(self, record: logging.LogRecord) -> str:
        color = self.LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def setup_logger(
    name: str = "freelance_bot_logger", level: int = logging.INFO
) -> logging.Logger:
    """Setup and return a logger"""

    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(level)
    custom_logger.propagate = False

    if not custom_logger.handlers:
        # prevent handler duplicating and create handler only if needed
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            ColoredFormatter(
                "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        custom_logger.addHandler(console_handler)

    return custom_logger


logger = setup_logger()
