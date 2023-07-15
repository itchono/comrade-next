from datetime import timezone
from zoneinfo import ZoneInfo

from aiohttp import ClientSession
from interactions import Client, Timestamp
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
    """

    db: Database
    tz: timezone = ZoneInfo(TIMEZONE)
    notify_on_restart: int = 0  # Channel ID to notify on restart
    http_session: ClientSession

    @property
    def start_timestamp(self) -> Timestamp | None:
        """
        Returns a timestamp object for the time
        the bot was started.
        """
        if not self.start_time:
            return None
        return Timestamp.fromdatetime(self.start_time)
