from interactions import (
    Extension,
    OptionType,
    SlashContext,
    is_owner,
    slash_command,
    slash_option,
)
from interactions.ext.prefixed_commands import prefixed_command

from comrade.core.updater import pull_repo, restart_process, update_packages


class Maintainence(Extension):
    """
    Commands used for maintainence of the bot.
    """

    @is_owner()
    @prefixed_command(help="Restarts the bot")
    async def restart(self, ctx: SlashContext):
        await ctx.send("Restarting...", ephemeral=True)
        restart_process(ctx.channel_id)

    @slash_command(description="Reruns pip install -e . --upgrade")
    async def reinstall(self, ctx: SlashContext):
        await ctx.defer(ephemeral=True)

        output_log = update_packages()
        await ctx.send(f"```...\n{output_log[-1900:]}\n```", ephemeral=True)

    @slash_command(description="Pulls the latest changes from the git repo")
    @slash_option(
        name="branch",
        description="The branch to pull from",
        required=False,
        opt_type=OptionType.STRING,
    )
    async def pull(self, ctx: SlashContext, branch: str = "main"):
        await ctx.send("Pulling...", ephemeral=True)
        pull_repo(branch=branch)


def setup(bot):
    Maintainence(bot)
