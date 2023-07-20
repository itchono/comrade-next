import re

from interactions import (
    ComponentContext,
    Extension,
    OptionType,
    SlashContext,
    User,
    component_callback,
    slash_command,
    slash_option,
)
from interactions.api.voice.audio import AudioVolume

from comrade.core.comrade_client import Comrade
from comrade.lib.discord_utils import DynamicPaginator

from .backend import SoundboardBackend


class Soundboard(Extension, SoundboardBackend):
    bot: Comrade

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="add_sound",
        sub_cmd_description="Add a sound to the soundboard (15 seconds max)",
        dm_permission=False,
    )
    @slash_option(
        name="url",
        description="Youtube URL to download sound from, or link to a sound file",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="name",
        description="The name of the sound",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="emoji",
        description="The emoji to use for the sound",
        required=False,
        opt_type=OptionType.STRING,
    )
    async def soundboard_add_sound(
        self, ctx: SlashContext, url: str, name: str, emoji: str = None
    ):
        await ctx.defer()
        audio = await self.create_soundboard_audio(ctx, url, name, emoji)

        await ctx.send(f"Soundboard audio `{audio.name}` added.")

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="remove_sound",
        sub_cmd_description="Remove a sound from the soundboard",
        dm_permission=False,
    )
    @slash_option(
        name="name",
        description="The name of the sound",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def soundboard_remove_sound(self, ctx: SlashContext, name: str):
        try:
            self.delete_soundboard_audio(ctx, name)
            await ctx.send(f"Soundboard audio `{name}` removed.")
        except ValueError as e:
            await ctx.send(f"Could not remove sound `{name}`: {e}")

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="connect",
        sub_cmd_description="Start a soundboard by connecting to your voice channel",
        dm_permission=False,
    )
    async def soundboard_connect(self, ctx: SlashContext):
        if isinstance(ctx.author, User):
            # This should never happen, but just in case
            await ctx.send("This command can only be used in a server.")

        audios = self.get_all_soundboard_audio_in_guild(ctx.guild_id)

        if audios is None:
            await ctx.send("No soundboard audio found.")
            return

        if ctx.voice_state is not None:
            if ctx.voice_state.channel == ctx.author.voice.channel:
                await ctx.send("Already connected to your voice channel.")
                return
            await ctx.voice_state.disconnect()

        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        await ctx.author.voice.channel.connect()

        paginator = DynamicPaginator(
            self.bot,
            await self.paginator_callback(ctx),
            maximum_pages=len(audios) // 20 + 1,
        )

        await paginator.send(ctx)

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="disconnect",
        sub_cmd_description="Stop the soundboard by disconnecting from your voice channel",
        dm_permission=False,
    )
    async def soundboard_disconnect(self, ctx: SlashContext):
        if ctx.voice_state is not None:
            await ctx.voice_state.disconnect()
            await ctx.send("Disconnected from voice channel.")
        else:
            await ctx.send("Not connected to a voice channel.", ephemeral=True)

    @component_callback(re.compile(r"soundboard:(\d+)"))
    async def soundboard_button_callback(self, ctx: ComponentContext):
        audio_id = ctx.custom_id.split(":")[1]

        audio = self.get_soundboard_audio(audio_id)

        if audio is None:
            await ctx.send(
                "Could not find soundboard audio. "
                "Try reconnecting the bot, as a sound may have been removed.",
                ephemeral=True,
            )
            return

        if ctx.voice_state is None:
            await ctx.send(
                "Not connected to a voice channel."
                " Call /soundboard connect to start the soundboard.",
                ephemeral=True,
            )
            return

        await ctx.edit_origin(content=f"Playing `{audio.name}`")
        await ctx.voice_state.play(AudioVolume(audio.blob_url))


def setup(bot):
    Soundboard(bot)
