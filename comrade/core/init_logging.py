# Taken from https://github.com/NAFTeam/Bot-Template
import logging
import os
import time
from os import getenv
from pathlib import Path
from typing import Optional

import arrow
from interactions import logger_name


class CustomLogger:
    """Log all errors to a file, and log all logging events to console"""

    def __init__(self):
        # Time format: YYYY-MM-DD HH:MM:SS <timezone>
        # Logger format: [TIME] [LEVEL]: MESSAGE

        timezone = getenv("COMRADE_TIMEZONE")

        self.formatter = logging.Formatter(
            "[%(asctime)s "
            + timezone
            + "] [%(name)s] [%(levelname)s]: %(message)s",
            "%Y-%m-%d %H:%M:%S",
        )

        def time_convert(*args) -> time.struct_time:
            # Convert time to tz specified in .env
            current_time = arrow.utcnow().to(timezone)
            return current_time.timetuple()

        self.formatter.converter = time_convert

        # Make sure the logs folder exists
        os.makedirs("./logs", exist_ok=True)

    def make_logger(self, log_name: str, output_filename: str):
        logger = logging.getLogger(log_name)
        logger.setLevel(logging.INFO)

        # log to console
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(self.formatter)
        console_handler.setLevel(logging.INFO)

        # log to file
        file_handler = MakeFileHandler(
            filepath=Path(f"./logs/{output_filename}.log"),
            encoding="utf-8",
        )
        file_handler.setFormatter(self.formatter)
        file_handler.setLevel(logging.INFO)

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


def init_logging(output_filename: str = logger_name):
    # Initialize formatter
    logger = CustomLogger()

    # Initialize logging for exceptions
    logger.make_logger(logger_name, output_filename)
