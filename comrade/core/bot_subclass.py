import logging
from typing import Any

import arrow
from aiohttp import ClientSession
from interactions import MISSING, Client, listen
from pymongo import MongoClient
from pymongo.database import Database

from comrade.core.configuration import (
    DEBUG_SCOPE,
    LOGGER_NAME,
    MONGODB_URI,
    TIMEZONE,
)
from comrade.core.const import CLIENT_INIT_KWARGS


class Comrade(Client):
    """
    Modified subclass of Client class to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - logging
    - uptime as Arrow type
    """

    db: Database
    timezone: str = TIMEZONE
    logger: logging.Logger = logging.getLogger("comrade")
    notify_on_restart: int = 0  # Channel ID to notify on restart

    def __init__(self, *args, **kwargs):
        if (debug_scope := DEBUG_SCOPE) == 0:
            debug_scope = MISSING

        # Init Interactions.py Bot class
        super().__init__(
            *args, debug_scope=debug_scope, **CLIENT_INIT_KWARGS, **kwargs
        )

        # Comrade-specific init
        mongo_client = MongoClient(MONGODB_URI)  # Connect to MongoDB
        self.db = mongo_client[mongo_client.list_database_names()[0]]
        self.logger.info(f"Connected to MongoDB, database name: {self.db.name}")

    @listen()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

        if self.notify_on_restart:
            await self.get_channel(self.notify_on_restart).send(
                f"Logged in as {self.user} has restarted."
            )

    @property
    def http_session(self) -> ClientSession:
        # Hack to get the aiohttp session from the http client
        return self.http._HTTPClient__session

    @property
    def start_time(self) -> arrow.Arrow:
        """
        The start time of the bot, as an Arrow instance.
        """
        if not (st := self._connection_state.start_time):
            return arrow.now(self.timezone)
        return arrow.Arrow.fromdatetime(st)

    # override extension loading to log when an extension is loaded
    def load_extension(
        self, name: str, package: str | None = None, **load_kwargs: Any
    ) -> None:
        super().load_extension(name, package, **load_kwargs)

        self.logger.info(f"Loaded extension: {name}")
