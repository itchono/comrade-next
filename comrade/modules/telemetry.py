from platform import python_version

from interactions import Embed, Extension, File, SlashContext, slash_command
from interactions.client.const import __api_version__
from interactions.client.const import __version__ as __interactions_version__

from comrade._version import __version__ as __comrade_version__
from comrade.core.bot_subclass import Comrade


class Telemetry(Extension):
    @slash_command(description="Gets the status of the bot")
    async def status(self, ctx: SlashContext):
        bot: Comrade = self.bot

        embed = Embed(title="Bot Status", color=0xD7342A)
        embed.set_author(name=bot.user.username, icon_url=bot.user.avatar.url)

        embed.add_field(
            name="Started",
            value=bot.start_time.humanize(),
            inline=True,
        )

        embed.add_field(
            name="Latency",
            value=f"{self.bot.latency * 1000:.2f} ms",
            inline=True,
        )

        embed.set_footer(
            text=f"Comrade v{__comrade_version__} | "
            f"Interactions v{__interactions_version__} | "
            f"Python v{python_version()} | "
            f"Discord API v{__api_version__}"
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
