import asyncio
import logging
from os import getenv
from urllib.parse import quote_plus

from interactions import (
    Client,
    Intents,
    SlashContext,
    listen,
    logger_name,
    slash_command,
    File,
)
from pymongo import MongoClient

from comrade.core.self_restarter import restart_process


class Comrade(Client):
    """
    Modified subclass of Client class to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - logging
    """

    db: MongoClient
    logger: logging.Logger = logging.getLogger(logger_name)

    def __init__(self, *args, **kwargs):
        # Init Interactions.py Bot class
        intents = Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.MESSAGE_CONTENT

        super().__init__(*args, intents=intents, auto_defer=True, **kwargs)

        # Comrade-specific init

        # Connect to MongoDB
        # must parse the password to avoid issues with special characters
        try:
            mongokey = kwargs["mongodb_key"]
        except KeyError:
            mongokey = getenv("MONGODB_KEY")

        self.db = MongoClient(quote_plus(mongokey))
        self.logger.info("Connected to MongoDB")

    @listen()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    @slash_command(description="Replies with pong!")
    async def ping(self, ctx: SlashContext):
        await ctx.send("Pong!", ephemeral=True)

    @slash_command(description="Restarts the bot.")
    async def restart(self, ctx: SlashContext):
        await ctx.send("Restarting...", ephemeral=True)
        restart_process()

    @slash_command(description="record some audio")
    async def record(self, ctx: SlashContext):
        voice_state = await ctx.author.voice.channel.connect()

        # Start recording
        await voice_state.start_recording()
        await asyncio.sleep(10)
        await voice_state.stop_recording()
        await ctx.send(
            files=[
                File(file, file_name=f"{user_id}.mp3")
                for user_id, file in voice_state.recorder.output.items()
            ]
        )
