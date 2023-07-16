import logging
from datetime import datetime
from logging.config import dictConfig
from pathlib import Path
from zoneinfo import ZoneInfo

from interactions import logger_name

from comrade.core.configuration import TIMEZONE


class ComradeLevelFilter(logging.Filter):
    """
    Turns logger names from
    e.g. `comrade.modules.reminder_cmds.backend` to
         `reminder_cmds`
    to improve readability.
    """

    def filter(self, record: logging.LogRecord) -> bool:
        if (
            record.name.startswith("comrade.")
            and len(record.name.split(".")) > 2
        ):
            # Remove comrade.*. from the logger name
            # as well as the module name
            record.name = record.name.split(".")[2]
        return True


class CustomFormatter(logging.Formatter):
    """
    Timezone-aware and ISO 8601-compliant formatter.

    Allows configuration of timezone according to the TIMEZONE variable in
    comrade/core/configuration.py.

    Does not accept datefmt as a parameter, as it is ignored in favor of the
    custom time format.
    """

    def formatTime(self, record: logging.LogRecord, datefmt: str = None) -> str:
        dt = datetime.fromtimestamp(record.created, tz=ZoneInfo(TIMEZONE))
        if datefmt:
            return dt.strftime(datefmt)

        return dt.isoformat(sep="T", timespec="milliseconds")


def init_logging(
    file_logging_level: int = logging.INFO,
    console_logging_level: int = logging.INFO,
):
    # Configure logging

    config_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "default": {
                "()": "comrade.core.logging_config.CustomFormatter",
                "format": (
                    "[%(asctime)s]"
                    " [%(name)s]"
                    " [%(levelname)s]: %(message)s"
                ),
            },
        },
        "filters": {
            "comrade_filter": {
                "()": "comrade.core.logging_config.ComradeLevelFilter",
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "formatter": "default",
                "level": console_logging_level,
                "filters": ["comrade_filter"],
            },
            "file": {
                "class": "logging.handlers.RotatingFileHandler",
                "formatter": "default",
                "maxBytes": 1024 * 256,  # 256 KB
                "backupCount": 5,
                "level": file_logging_level,
                "filename": "./logs/comrade.log",
                "encoding": "utf-8",
            },
        },
        "loggers": {
            # Configure package level logger
            # Other files in the package will inherit this configuration
            "comrade": {
                "handlers": ["console", "file"],
                "level": min(file_logging_level, console_logging_level),
                "propagate": False,
            },
            # Configure interactions.py logger
            logger_name: {
                "handlers": ["console", "file"],
                "level": min(file_logging_level, console_logging_level),
                "propagate": False,
            },
        },
    }

    # Make sure the logs folder exists
    Path(config_dict["handlers"]["file"]["filename"]).parent.mkdir(
        parents=True, exist_ok=True
    )

    dictConfig(config_dict)
