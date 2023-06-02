from interactions import Extension, SlashContext, slash_command

from comrade.core.updater import pull_repo, restart_process, update_packages


class Maintainence(Extension):
    @slash_command(description="Restarts the bot.")
    async def restart(self, ctx: SlashContext):
        # Check that the bot owner is running this command
        if ctx.author.id not in self.bot.owner_ids:
            await ctx.send("You can't do that!", ephemeral=True)
            return

        await ctx.send("Restarting...", ephemeral=True)
        restart_process()

    @slash_command(description="Reruns pip install -e . --upgrade")
    async def reinstall(self, ctx: SlashContext):
        # Check that the bot owner is running this command
        if ctx.author.id not in self.bot.owner_ids:
            await ctx.send("You can't do that!", ephemeral=True)
            return

        await ctx.send("Reinstalling...", ephemeral=True)
        update_packages()

    @slash_command(description="Pulls the latest changes from the git repo")
    async def pull(self, ctx: SlashContext):
        # Check that the bot owner is running this command
        if ctx.author.id not in self.bot.owner_ids:
            await ctx.send("You can't do that!", ephemeral=True)
            return

        await ctx.send("Pulling...", ephemeral=True)
        pull_repo()


def setup(bot):
    Maintainence(bot)
