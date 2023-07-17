from logging import getLogger

import orjson
from aiohttp import ClientSession
from interactions import Activity, ActivityType, listen
from pymongo import MongoClient

from comrade._version import __version__
from comrade.core.augmentations import AugmentedClient
from comrade.core.configuration import (
    MONGODB_URI,
    RELAY_GUILD_ID,
    TEST_GUILD_ID,
)
from comrade.core.const import CLIENT_INIT_KWARGS
from comrade.core.relay_system import RelayMixin
from comrade.lib.discord_utils import messageable_from_context_id

logger = getLogger(__name__)


class Comrade(
    AugmentedClient,
    RelayMixin,
):
    """
    Modified subclass of Client class to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - aiohttp ClientSession

    Overrides
    ---------
    - Turns off on_..._completion listeners from interactions.py
    """

    def __init__(self, *args, **kwargs):
        # Init Interactions.py Bot class
        super().__init__(
            *args,
            debug_scope=TEST_GUILD_ID,
            activity=Activity.create(
                name="the proletariat", type=ActivityType.WATCHING
            ),
            **CLIENT_INIT_KWARGS,
            **kwargs,
        )

        logger.info(f"Starting Comrade version {__version__}")

        # Comrade-specific init
        mongo_client = MongoClient(MONGODB_URI)  # Connect to MongoDB
        self.db = mongo_client[mongo_client.list_database_names()[0]]
        logger.info(f"Connected to MongoDB, database name: {self.db.name}")

        if kwargs.get("notify_on_restart"):
            self.notify_on_restart = kwargs["notify_on_restart"]

    @listen()
    async def on_login(self):
        """
        Hook onto the first even in the asyncio loop in order
        to initialize the aiohttp ClientSession.
        """
        self.http_session = ClientSession(json_serialize=orjson.dumps)

    @listen()
    async def on_ready(self):
        # Set up relay guild
        await self.init_relay(RELAY_GUILD_ID)

        logger.info(f"Bot is Ready. Logged in as {self.user} ({self.user.id})")

        # Notify on restart, if enabled
        if self.notify_on_restart:
            logger.info(
                f"Notifying on restart: Channel/User with ID {self.notify_on_restart}"
            )

            try:
                restart_msgable = await messageable_from_context_id(
                    self.notify_on_restart, self
                )
                await restart_msgable.send(
                    f"Bot has restarted, current version is {__version__}."
                )
            except ValueError:
                logger.warning(
                    f"Could not find channel or user with ID {self.notify_on_restart}"
                )

    @listen(disable_default_listeners=True)
    async def on_command_completion(self, *args, **kwargs):
        ...

    @listen(disable_default_listeners=True)
    async def on_component_completion(self, *args, **kwargs):
        ...

    @listen(disable_default_listeners=True)
    async def on_autocomplete_completion(self, *args, **kwargs):
        ...

    @listen(disable_default_listeners=True)
    async def on_modal_completion(self, *args, **kwargs):
        ...
