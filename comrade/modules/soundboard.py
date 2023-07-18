from interactions import (
    ActiveVoiceState,
    Button,
    ButtonStyle,
    ComponentContext,
    Extension,
    SlashContext,
    User,
    component_callback,
    slash_command,
)
from interactions.api.voice.audio import AudioVolume

from comrade.core.comrade_client import Comrade


class VoiceRecorder(Extension):
    bot: Comrade
    voice_state: ActiveVoiceState = None

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

        if self.voice_state is not None:
            await self.voice_state.disconnect()
            self.voice_state = None

        self.voice_state = await ctx.author.voice.channel.connect()

        button = Button(
            custom_id="sfx1", style=ButtonStyle.PRIMARY, label="SFX 1"
        )
        await ctx.send("Connected to voice channel.", components=[button])

    @slash_command(
        name="soundboard",
        description="soundboard system",
        sub_cmd_name="disconnect",
        sub_cmd_description="Stop the soundboard by disconnecting from your voice channel",
        dm_permission=False,
    )
    async def soundboard_disconnect(self, ctx: SlashContext):
        if self.voice_state is not None:
            await self.voice_state.disconnect()
            self.voice_state = None
        await ctx.send("Disconnected from voice channel.")

    @component_callback("sfx1")
    async def sfx1(self, ctx: ComponentContext):
        if self.voice_state is None:
            await ctx.send("Not connected to a voice channel.")
            return

        await ctx.send("Playing SFX1", delete_after=1)

        audio = AudioVolume(
            "https://cdn.discordapp.com/attachments/753461808139862038/1110774397238784000/Patrick_thats_a_Blue_Eyes_White_Dragon.mp3"
        )
        await self.voice_state.play(audio)


def setup(bot):
    VoiceRecorder(bot)
