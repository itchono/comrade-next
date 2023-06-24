from interactions import (
    Embed,
    Extension,
    File,
    OptionType,
    SlashContext,
    slash_command,
    slash_option,
)

from comrade.core.bot_subclass import Comrade


class Utils(Extension):
    bot: Comrade

    @slash_command(
        description="Mirror an existing asset on the internet (usually an image) to Discord)"
    )
    @slash_option(
        name="url",
        description="The URL to mirror",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def mirror_to_discord(self, ctx: SlashContext, url: str):
        mirrored_url = await self.bot.relay.mirror_blob(
            url, self.bot.db.relayBlobs
        )

        await ctx.send(f"`{mirrored_url}`\n{mirrored_url}")


def setup(bot):
    Utils(bot)
