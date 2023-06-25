# Taken from https://github.com/NAFTeam/Bot-Template
import logging
import time
from pathlib import Path
from typing import Optional

import arrow

from comrade.core.configuration import TIMEZONE


class CustomLogger:
    """Log all errors to a file, and log all logging events to console"""

    def __init__(self):
        # Time format: YYYY-MM-DD HH:MM:SS <timezone>
        # Logger format: [TIME] [LEVEL]: MESSAGE

        timezone = TIMEZONE

        self.formatter = logging.Formatter(
            "[%(asctime)s " + timezone + "] [%(levelname)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        def time_convert(*_) -> time.struct_time:
            # Convert time to tz specified in .env
            current_time = arrow.utcnow().to(timezone)
            return current_time.timetuple()

        self.formatter.converter = time_convert

        # Make sure the logs folder exists
        Path("./logs").mkdir(parents=True, exist_ok=True)

    def make_logger(
        self,
        log_name: str,
        file_logging_level: int = logging.INFO,
        console_logging_level: int = logging.INFO,
    ):
        logger = logging.getLogger(log_name)
        logger.setLevel(min(file_logging_level, console_logging_level))

        # log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        console_handler.setLevel(console_logging_level)

        # log to file
        file_handler = MakeFileHandler(
            filepath=Path(f"./logs/{log_name}.log"),
            encoding="utf-8",
        )
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(file_logging_level)

        # add bother handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)


class MakeFileHandler(logging.FileHandler):
    """Subclass of logging.FileHandler which makes sure the folder is created"""

    def __init__(
        self,
        filepath: Path,
        mode: str = "a",
        encoding: Optional[str] = None,
        delay: bool = False,
    ):
        # create the folder if it does not exist already
        filepath.parent.mkdir(parents=True, exist_ok=True)
        logging.FileHandler.__init__(self, filepath, mode, encoding, delay)


def init_logging(
    logger_name: str,
    file_logging_level: int = logging.INFO,
    console_logging_level: int = logging.INFO,
):
    # Initialize formatter
    logger = CustomLogger()

    # Initialize logging for exceptions
    logger.make_logger(logger_name, file_logging_level, console_logging_level)
