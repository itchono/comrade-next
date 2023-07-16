import asyncio
import logging
from argparse import ArgumentParser
from pathlib import Path

from interactions.ext import hybrid_commands, prefixed_commands

from comrade.core.comrade_client import Comrade
from comrade.core.configuration import ACCENT_COLOUR, BOT_TOKEN, DEV_MODE
from comrade.core.logging_config import init_logging


def main(args: list[str] = None, test_mode: bool = False) -> Comrade:
    """
    Starts the bot and returns it.

    Parameters
    ----------
    args : list[str], optional
        The command line arguments to parse. If not provided, the arguments
        will be read from sys.argv.

    test_mode: bool, optional
        Whether to run the bot in test mode. If True, the bot will not
        try to initialize a new asyncio event loop.

    Returns
    -------
    Comrade
        The bot instance.

    """

    # Parse command line arguments
    parser = ArgumentParser(description="Comrade Bot")
    parser.add_argument(
        "--notify_channel",
        type=int,
        help="Send a message to the channel with this ID after startup",
        default=0,
    )
    args = parser.parse_args(args)

    init_logging(
        file_logging_level=logging.INFO,
        console_logging_level=logging.INFO,
    )

    bot = Comrade(notify_on_restart=args.notify_channel)

    prefixed_commands.setup(bot)
    hybrid_commands.setup(bot)
    # Load all extensions in the comrade/modules directory
    for module in Path(__file__).parent.glob("modules/*"):
        # Skip all dunder files
        if module.stem.startswith("__"):
            continue
        bot.load_extension(f"comrade.modules.{module.stem}")

    help_cmd = prefixed_commands.help.PrefixedHelpCommand(
        bot, embed_color=ACCENT_COLOUR
    )
    help_cmd.register()

    logger = logging.getLogger(__name__)

    if DEV_MODE:
        bot.load_extension("interactions.ext.jurigged")
        logger.warning("Running in dev mode.")

    if test_mode:
        asyncio.create_task(bot.login(token=BOT_TOKEN))
        asyncio.create_task(bot.start_gateway())
    else:
        bot.start(token=BOT_TOKEN)
    return bot


if __name__ == "__main__":
    main()
