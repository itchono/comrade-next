import logging
from os import getenv
from typing import Any
from urllib.parse import quote_plus

import arrow
from aiohttp import ClientSession
from interactions import MISSING, Client, listen, logger_name
from pymongo import MongoClient

from comrade.core.const import CLIENT_INIT_KWARGS


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

    def __init__(self, *args, **kwargs):
        if (debug_scope := getenv("COMRADE_DEBUG_SCOPE")) is None:
            debug_scope = MISSING

        # Init Interactions.py Bot class
        super().__init__(
            *args, debug_scope=debug_scope, **CLIENT_INIT_KWARGS, **kwargs
        )

        # Comrade-specific init

        # Connect to MongoDB
        # must parse the password to avoid issues with special characters
        try:
            mongokey = kwargs["mongodb_key"]
        except KeyError:
            mongokey = getenv("COMRADE_MONGODB_KEY")

        try:
            timezone = kwargs["timezone"]
        except KeyError:
            timezone = getenv("COMRADE_TIMEZONE")

        self.db = MongoClient(quote_plus(mongokey))
        self.logger.info("Connected to MongoDB")
        self.timezone = timezone

    @listen()
    async def on_ready(self):
        self.logger.info(f"Logged in as {self.user} ({self.user.id})")

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
