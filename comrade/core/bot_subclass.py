import logging
from os import getenv
from typing import Any
from urllib.parse import quote_plus

from arrow import Arrow, now
from interactions import Client, Intents, listen, logger_name
from pymongo import MongoClient


class Comrade(Client):
    """
    Modified subclass of Client class to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - logging
    - uptime
    """

    db: MongoClient
    timezone: str
    logger: logging.Logger = logging.getLogger(logger_name)
    start_time: Arrow = now()

    def __init__(self, timezone: str, *args, **kwargs):
        # Init Interactions.py Bot class
        intents = (
            Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.MESSAGE_CONTENT
        )

        super().__init__(
            *args,
            intents=intents,
            auto_defer=True,
            delete_unused_application_cmds=True,
            sync_ext=True,
            **kwargs,
        )

        # Comrade-specific init

        # Connect to MongoDB
        # must parse the password to avoid issues with special characters
        try:
            mongokey = kwargs["mongodb_key"]
        except KeyError:
            mongokey = getenv("MONGODB_KEY")

        self.db = MongoClient(quote_plus(mongokey))
        self.logger.info("Connected to MongoDB")
        self.timezone = timezone

    @listen()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

    # Log extension loading
    def load_extension(
        self, name: str, package: str | None = None, **load_kwargs: Any
    ) -> None:
        super().load_extension(name, package, **load_kwargs)

        self.logger.info(f"Loaded extension: {name}")
