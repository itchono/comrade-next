import asyncio
from io import BytesIO

from arrow import now
from interactions import (
    Extension,
    File,
    OptionType,
    SlashContext,
    User,
    slash_command,
    slash_option,
)
from pydub import AudioSegment

from comrade.core.bot_subclass import Comrade


class VoiceRecorder(Extension):
    bot: Comrade

    @slash_command(description="record some audio", dm_permission=False)
    @slash_option(
        name="duration",
        description="duration to record for (seconds)",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
        max_value=30,
    )
    async def record(self, ctx: SlashContext, duration: int):
        if isinstance(ctx.author, User):
            # This should never happen, but just in case
            await ctx.send("This command can only be used in a server.")

        voice_state = await ctx.author.voice.channel.connect()

        # Start recording
        await voice_state.start_recording()
        await asyncio.sleep(duration)
        await voice_state.stop_recording()

        audio_clips = voice_state.recorder.output.values()

        # Overlay all clips together
        audio = AudioSegment.silent(duration=duration * 1000)
        for clip_file in audio_clips:
            clip = AudioSegment.from_file(clip_file, format="mp3")
            audio = audio.overlay(clip)

        # Turn the audio file into a BytesIO object and send it
        io_obj = BytesIO()
        audio.export(io_obj, format="mp3")
        io_obj.seek(0)

        recording_timestamp = now(self.bot.timezone).format(
            "YYYY-MM-DD_HH-mm-ss"
        )

        await ctx.send(
            file=File(io_obj, f"Recording_{recording_timestamp}.mp3")
        )

        await voice_state.disconnect()


def setup(bot):
    VoiceRecorder(bot)
