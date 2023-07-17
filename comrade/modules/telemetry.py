from io import StringIO
from logging import getLogger
from platform import python_version

from interactions import (
    Embed,
    Extension,
    File,
    OptionType,
    SlashContext,
    TimestampStyles,
    slash_command,
    slash_option,
)
from interactions.client.const import __version__ as __interactions_version__

from comrade._version import __version__ as __comrade_version__
from comrade.core.comrade_client import Comrade
from comrade.core.configuration import ACCENT_COLOUR
from comrade.core.updater import get_current_branch

logger = getLogger(__name__)


class Telemetry(Extension):
    bot: Comrade

    @slash_command(description="Gets the status of the bot")
    async def status(self, ctx: SlashContext):
        embed = Embed(title="Bot Status", color=ACCENT_COLOUR)
        embed.set_author(
            name=self.bot.user.username, icon_url=self.bot.user.avatar.url
        )

        last_restart_str = (
            f"{self.bot.start_timestamp.format(TimestampStyles.RelativeTime)}\n"
            f"at {self.bot.start_timestamp.format(TimestampStyles.ShortDateTime)}"
        )

        embed.add_field(
            name="Last Restart",
            value=last_restart_str,
            inline=True,
        )

        embed.add_field(
            name="Latency",
            value=f"{self.bot.latency * 1000:.2f} ms",
            inline=True,
        )

        # Drop the +... from the version
        comrade_version = __comrade_version__.split("+")[0]

        embed.set_footer(
            text=f"Comrade v{comrade_version} on "
            f"{get_current_branch()} | "
            f"Interactions v{__interactions_version__} | "
            f"Python v{python_version()}"
        )

        await ctx.send(embed=embed)

    @slash_command(
        description="Gets the log for the bot",
    )
    @slash_option(
        name="lines",
        description="send only the last N lines",
        required=False,
        opt_type=OptionType.INTEGER,
        min_value=1,
    )
    async def log(self, ctx: SlashContext, lines: int = None):
        log_path = ctx.bot.logger.handlers[1].baseFilename  # janky but it works

        if lines is not None:
            with open(log_path, "r") as log_file:
                log_lines = log_file.readlines()[-lines:]

            joined_lines = "".join(log_lines)

            log_file = File(StringIO(joined_lines), file_name="comrade_log.txt")
        else:
            # full log
            log_file = File(log_path, file_name="comrade_log.txt")
        await ctx.send(file=log_file, ephemeral=True)


def setup(bot):
    Telemetry(bot)
