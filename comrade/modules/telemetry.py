from platform import python_version

import arrow
from interactions import Embed, Extension, File, SlashContext, slash_command
from interactions.client.const import __version__ as __interactions_version__

from comrade._version import __version_tuple__ as __comrade_version__
from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import ACCENT_COLOUR
from comrade.lib.updater_utils import get_current_branch


class Telemetry(Extension):
    bot: Comrade

    @slash_command(description="Gets the status of the bot")
    async def status(self, ctx: SlashContext):
        embed = Embed(title="Bot Status", color=ACCENT_COLOUR)
        embed.set_author(
            name=self.bot.user.username, icon_url=self.bot.user.avatar.url
        )

        embed.add_field(
            name="Uptime",
            value=arrow.now(self.bot.timezone).humanize(
                self.bot.start_time, only_distance=True
            ),
            inline=True,
        )

        embed.add_field(
            name="Latency",
            value=f"{self.bot.latency * 1000:.2f} ms",
            inline=True,
        )
        comrade_version = ".".join(map(str, __comrade_version__[:4]))

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
    async def view_log(self, ctx: SlashContext):
        log_path = self.bot.logger.handlers[1].baseFilename

        log_file = File(log_path, file_name="comrade_log.txt")
        await ctx.send(file=log_file, ephemeral=True)


def setup(bot):
    Telemetry(bot)
