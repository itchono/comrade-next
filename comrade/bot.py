import logging
from argparse import ArgumentParser
from pathlib import Path

from interactions import logger_name as interactions_logger_name
from interactions.client.const import CLIENT_FEATURE_FLAGS
from interactions.ext import prefixed_commands

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import BOT_TOKEN, LOGGER_NAME
from comrade.core.init_logging import init_logging


def main(token: str = None):
    # Parse command line arguments
    parser = ArgumentParser(description="Comrade Bot")
    parser.add_argument(
        "--notify_channel",
        type=int,
        help="Send a message to the channel with this ID after startup",
    )
    parser.parse_args()

    # Load env vars, if needed
    if token is None:
        token = BOT_TOKEN

    init_logging(
        interactions_logger_name,
        console_logging_level=logging.WARNING,
        file_logging_level=logging.INFO,
    )
    init_logging(
        LOGGER_NAME,
        file_logging_level=logging.INFO,
        console_logging_level=logging.INFO,
    )

    bot = Comrade()

    prefixed_commands.setup(bot)

    # Temp workaround for discord API image upload bug
    CLIENT_FEATURE_FLAGS["FOLLOWUP_INTERACTIONS_FOR_IMAGES"] = True

    # Load all extensions in the comrade/modules directory
    for module in Path(__file__).parent.glob("modules/*.py"):
        # Skip __init__.py
        if module.stem == "__init__":
            continue
        bot.load_extension(f"comrade.modules.{module.stem}")

    bot.load_extension("interactions.ext.jurigged")

    bot.start(token=token)


if __name__ == "__main__":
    main()
