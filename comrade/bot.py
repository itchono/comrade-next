import logging
from argparse import ArgumentParser
from pathlib import Path

from interactions import logger_name
from interactions.client.const import CLIENT_FEATURE_FLAGS
from interactions.ext import prefixed_commands

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import ACCENT_COLOUR, BOT_TOKEN, DEBUG
from comrade.core.init_logging import init_logging


def main(token: str = None):
    # Parse command line arguments
    parser = ArgumentParser(description="Comrade Bot")
    parser.add_argument(
        "--notify_channel",
        type=int,
        help="Send a message to the channel with this ID after startup",
        default=0,
    )
    args = parser.parse_args()

    if token is None:
        token = BOT_TOKEN

    init_logging(
        logger_name,
        file_logging_level=logging.INFO,
        console_logging_level=logging.INFO,
    )

    bot = Comrade(notify_on_restart=args.notify_channel)

    # Temp workaround for discord API image upload bug
    CLIENT_FEATURE_FLAGS["FOLLOWUP_INTERACTIONS_FOR_IMAGES"] = True

    prefixed_commands.setup(bot)
    # Load all extensions in the comrade/modules directory
    for module in Path(__file__).parent.glob("modules/*.py"):
        # Skip __init__.py
        if module.stem == "__init__":
            continue
        bot.load_extension(f"comrade.modules.{module.stem}")

    help_cmd = prefixed_commands.help.PrefixedHelpCommand(
        bot, embed_color=ACCENT_COLOUR
    )
    help_cmd.register()

    if DEBUG:
        bot.load_extension("interactions.ext.jurigged")

    bot.start(token=token)


if __name__ == "__main__":
    main()
