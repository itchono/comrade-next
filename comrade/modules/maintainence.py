from interactions import (
    Extension,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
)

from comrade.core.updater import pull_repo, restart_process, update_packages
from comrade.lib.checks import is_owner


class Maintainence(Extension):
    """
    Commands used for maintainence of the bot.
    """

    @slash_command(description="Restarts the bot.")
    async def restart(self, ctx: SlashContext):
        if not is_owner(ctx):
            return await ctx.send("You are not the bot owner.", ephemeral=True)

        await ctx.send("Restarting...", ephemeral=True)
        restart_process()

    @slash_command(description="Reruns pip install -e . --upgrade")
    async def reinstall(self, ctx: SlashContext):
        await ctx.defer(ephemeral=True)
        if not is_owner(ctx):
            return await ctx.send("You are not the bot owner.", ephemeral=True)

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
        if not is_owner(ctx):
            return await ctx.send("You are not the bot owner.", ephemeral=True)

        await ctx.send("Pulling...", ephemeral=True)
        pull_repo(branch=branch)


def setup(bot):
    Maintainence(bot)
