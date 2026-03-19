"""Logger utility for colored console output

Provides a colored logger instance with custom SUCCESS level and formatted output
using colorama for cross-platform color support.
"""

import logging
import sys

from colorama import Fore, Style, init

init(autoreset=True)  # autoreset string color


class ColoredFormatter(logging.Formatter):
    """
    Custom logging formatter with color-coded log levels.

    Adds color to log output for better visibility and debugging:
    - DEBUG: Cyan
    - INFO: White
    - SUCCESS: Green (custom level at 25)
    - WARNING: Yellow
    - ERROR: Red
    - CRITICAL: Magenta
    """

    # set success level
    SUCCESS = 25  # between INFO and WARNING
    logging.addLevelName(SUCCESS, "SUCCESS")

    LEVEL_COLORS: dict[int, str] = {  # color palette
        logging.DEBUG: Fore.LIGHTCYAN_EX,
        logging.INFO: Fore.LIGHTWHITE_EX,
        SUCCESS: Fore.LIGHTGREEN_EX,
        logging.WARNING: Fore.LIGHTYELLOW_EX,
        logging.ERROR: Fore.LIGHTRED_EX,
        logging.CRITICAL: Fore.LIGHTMAGENTA_EX,
    }

    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with color based on log level.

        Args:
            record: LogRecord to format

        Returns:
            str: Formatted and colored log message
        """

        color = self.LEVEL_COLORS.get(record.levelno, "")
        message = super().format(record)
        return f"{color}{message}{Style.RESET_ALL}"


def setup_logger(
    name: str = "freelance_bot_logger",
    level: int = logging.INFO,
    log_to_file: bool = True,  # if u need save log to file - set True
    log_file: str = "bot.log",
) -> logging.Logger:
    """
    Setup and configure a logger instance with console and optional file output.

    Creates a logger with:
    - Colored console output (uses ColoredFormatter)
    - Optional file logging
    - Specified logging level

    Args:
        name: Logger name (default: "freelance_bot_logger")
        level: Logging level (default: logging.INFO)
        log_to_file: Whether to also log to file (default: True)
        log_file: File path for log output (default: "bot.log")

    Returns:
        logging.Logger: Configured logger instance ready for use
    """

    custom_logger = logging.getLogger(name)
    custom_logger.setLevel(level)
    custom_logger.propagate = False

    if not custom_logger.handlers:
        # prevent handler duplicating and create handler only if needed
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(
            ColoredFormatter(
                "%(asctime)s.%(msecs)03d [%(levelname)s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        custom_logger.addHandler(console_handler)

    if log_to_file:
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter(
                "%(asctime)s [%(levelname)-7s] %(name)s: %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
        )
        custom_logger.addHandler(file_handler)

    def success(
        self: logging.Logger, message: str, *args: object, **kwargs: object
    ) -> None:
        """
        Log a success message at custom SUCCESS level (25).

        Args:
            self: Logger instance
            message: Message to log
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
        """

        if self.isEnabledFor(ColoredFormatter.SUCCESS):
            self._log(ColoredFormatter.SUCCESS, message, args, **kwargs)  # pylint: disable=protected-access

    logging.Logger.success = success

    return custom_logger


logger: logging.Logger = setup_logger()
