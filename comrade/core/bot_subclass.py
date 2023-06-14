from zoneinfo import ZoneInfo

import arrow
import orjson
from aiohttp import ClientSession
from interactions import MISSING, Client, listen
from pymongo import MongoClient
from pymongo.database import Database

from comrade import __version__
from comrade.core.configuration import DEBUG_SCOPE, MONGODB_URI, TIMEZONE
from comrade.core.const import CLIENT_INIT_KWARGS


class Comrade(Client):
    """
    Modified subclass of Client class to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - aiohttp ClientSession
    - uptime as Arrow type

    Overrides
    ---------
    - Turns off on_..._completion listeners from interactions.py
    """

    db: Database
    timezone: str = TIMEZONE
    notify_on_restart: int = 0  # Channel ID to notify on restart
    http_session: ClientSession

    def __init__(self, *args, **kwargs):
        if (debug_scope := DEBUG_SCOPE) == 0:
            debug_scope = MISSING

        # Init Interactions.py Bot class
        super().__init__(
            *args,
            debug_scope=debug_scope,
            **CLIENT_INIT_KWARGS,
            **kwargs,
        )

        self.logger.info(f"Starting Comrade version {__version__}")

        # Comrade-specific init
        mongo_client = MongoClient(MONGODB_URI)  # Connect to MongoDB
        self.db = mongo_client[mongo_client.list_database_names()[0]]
        self.logger.info(f"Connected to MongoDB, database name: {self.db.name}")

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
        self.logger.info(
            f"Bot is Ready. Logged in as {self.user} ({self.user.id})"
        )

        if self.notify_on_restart:
            self.logger.info(
                f"Notifying on restart: Channel/User with ID {self.notify_on_restart}"
            )

            restart_msg = (
                f"Bot has restarted, current version is {__version__}."
            )

            if channel := self.get_channel(self.notify_on_restart):
                await channel.send(restart_msg)
            elif user := self.get_user(self.notify_on_restart):
                await user.send(restart_msg)
            else:
                self.logger.warning(
                    f"Could not find channel or user with ID {self.notify_on_restart}"
                )

    @listen(disable_default_listeners=True)
    async def on_command_completion(self, *args, **kwargs):
        pass

    @listen(disable_default_listeners=True)
    async def on_component_completion(self, *args, **kwargs):
        pass

    @listen(disable_default_listeners=True)
    async def on_autocomplete_completion(self, *args, **kwargs):
        pass

    @listen(disable_default_listeners=True)
    async def on_modal_completion(self, *args, **kwargs):
        pass

    @property
    def start_time(self) -> arrow.Arrow:
        """
        The start time of the bot, as an Arrow instance.

        Timezone is set to the bot's timezone.
        """
        if not (st := self._connection_state.start_time):
            return arrow.now(self.timezone)

        # ensure that st is localized to our timezone (because it defaults to whatever
        # the system timezone is)
        return arrow.Arrow.fromdatetime(st.astimezone(ZoneInfo(self.timezone)))
