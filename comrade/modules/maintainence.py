from interactions import Extension, SlashContext, check, is_owner
from interactions.ext.prefixed_commands import PrefixedContext, prefixed_command

from comrade._version import __version__
from comrade.core.updater import (
    check_updates_on_branch,
    get_current_branch,
    get_current_commit_hash,
    pull_repo,
    restart_process,
    update_packages,
)
from comrade.lib.discord_utils import context_id


class Maintainence(Extension):
    """
    Commands used for maintainence of the bot.
    """

    @prefixed_command(help="Restarts the bot")
    @check(is_owner())
    async def restart(self, ctx: SlashContext):
        """
        Restarts the bot, notifying the channel it was launched from.

        Stops the bot to ensure a clean restart.
        (stops listening for new commands)
        """
        await ctx.send("Restarting...", ephemeral=True)
        await self.bot.stop()
        self.bot.logger.warning("RESTARTING BOT!")
        restart_process(context_id(ctx))

    @prefixed_command(help="Checks for updates on this git branch")
    async def check_updates(self, ctx: SlashContext):
        """
        Checks for updates on this git branch.
        """
        updates = check_updates_on_branch()

        if "Your branch is up to date" in updates:
            await ctx.send(
                f"No updates available. Current Version is {__version__}"
                f"\n```\n{updates}\n```"
            )
        else:
            await ctx.send(
                f"Changes found. (Current Version is {__version__})"
                f"```\n{updates}\n```"
                f"{self.bot.user.mention} `install_updates` to install the update."
            )

    @prefixed_command(help="Pulls updates, reinstalls, and restarts")
    @check(is_owner())
    async def install_updates(
        self, ctx: PrefixedContext, branch_name: str = get_current_branch()
    ):
        """
        Pulls updates from GitHub, reinstalls the bot package,
        and restarts it.

        Parameters
        ----------
        branch_name : str
            The branch to pull from, defaults to current branch

        Emits a warning if there are no updates available.
        """

        if branch_name != get_current_branch():
            await ctx.send(f"Switching branches to {branch_name}...")

        current_commit_hash = get_current_commit_hash()
        pull_repo(branch=branch_name)
        new_commit_hash = get_current_commit_hash()

        if current_commit_hash == new_commit_hash:
            await ctx.send(
                "No updates have been downloaded, "
                f"still at commit hash `{current_commit_hash}`"
            )
        else:
            await ctx.send(
                "Updates have been downloaded: "
                f"`{current_commit_hash}` -> `{new_commit_hash}`"
            )

        # Reinstall the bot package
        await ctx.send("Installing bot package...")
        output_log = update_packages()

        last_couple_of_lines = "\n".join(output_log.split("\n")[-5:])

        await ctx.send(f"```...\n{last_couple_of_lines}\n```")

        await ctx.send("Restarting bot...", ephemeral=True)
        await self.bot.stop()
        self.bot.logger.warning("RESTARTING BOT FOR NEW UPDATE...")
        restart_process(context_id(ctx))


def setup(bot):
    Maintainence(bot)
