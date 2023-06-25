from zoneinfo import ZoneInfo

import arrow
from aiohttp import ClientSession
from interactions import Client
from pymongo.database import Database

from comrade.core.configuration import (
    TIMEZONE,
)


class AugmentedClient(Client):
    """
    Additional class attributes to augment
    interations.Client

    Extra Additions

    ---------------
    - MongoDB connection
    - Configuration store
    - aiohttp ClientSession
    - uptime as Arrow type
    """

    db: Database
    timezone: str = TIMEZONE
    notify_on_restart: int = 0  # Channel ID to notify on restart
    http_session: ClientSession

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
