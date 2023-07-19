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
    spread_to_rows,
)
from interactions.api.voice.audio import AudioVolume

from comrade.core.comrade_client import Comrade

from .backend import SoundboardBackend


class Soundboard(Extension, SoundboardBackend):
    bot: Comrade

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="addsound",
        sub_cmd_description="Add a sound to the soundboard",
        dm_permission=False,
    )
    @slash_option(
        name="url",
        description="The url of the youtube video",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="name",
        description="The name of the sound",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def soundboard_addsound(self, ctx: SlashContext, url: str, name: str):
        await ctx.defer()
        audio = await self.create_soundboard_audio(ctx, url, name)

        await ctx.send(f"Soundboard audio `{audio.name}` added.")

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

        if ctx.voice_state is not None:
            await ctx.voice_state.disconnect()

        if ctx.author.voice is None:
            await ctx.send("You are not in a voice channel.")
            return

        await ctx.author.voice.channel.connect()

        audios = self.get_all_soundboard_audio_in_guild(ctx.guild_id)

        if audios is None:
            await ctx.send("No soundboard audio found.")
            return

        # trim to the first 25 for now, work on pagination later
        components = spread_to_rows(*[audio.button for audio in audios[:25]])

        await ctx.send("Connected to voice channel.", components=components)

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

    @component_callback(re.compile(r"soundboard:(\d+)"))
    async def soundboard_button_callback(self, ctx: ComponentContext):
        audio_id = ctx.custom_id.split(":")[1]

        audio = self.get_soundboard_audio(audio_id)

        if ctx.voice_state is None:
            await ctx.send("Not connected to a voice channel.")
            return

        await ctx.edit_origin(content=f"Playing `{audio.name}`")
        await ctx.voice_state.play(AudioVolume(audio.blob_url))


def setup(bot):
    Soundboard(bot)
