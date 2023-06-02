from interactions import Extension, SlashContext, is_owner, slash_command

from comrade.core.updater import pull_repo, restart_process, update_packages


class Maintainence(Extension):
    @is_owner()
    @slash_command(description="Restarts the bot.")
    async def restart(self, ctx: SlashContext):
        await ctx.send("Restarting...", ephemeral=True)
        restart_process()

    @is_owner()
    @slash_command(description="Reruns pip install -e . --upgrade")
    async def reinstall(self, ctx: SlashContext):
        output_log = update_packages()
        await ctx.send(f"```\n{output_log}\n```", ephemeral=True)

    @is_owner()
    @slash_command(description="Pulls the latest changes from the git repo")
    async def pull(self, ctx: SlashContext):
        await ctx.send("Pulling...", ephemeral=True)
        pull_repo()


def setup(bot):
    Maintainence(bot)
