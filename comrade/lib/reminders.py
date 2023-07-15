from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone, tzinfo

from bson import ObjectId
from dateutil.tz import tzlocal
from interactions import (
    BaseContext,
    ContextMenuContext,
    Timestamp,
)
from interactions.ext.hybrid_commands import HybridContext
from interactions.ext.prefixed_commands import PrefixedContext
from timelength import TimeLength

from comrade.lib.discord_utils import context_id


@dataclass
class Reminder:
    """
    Representation of a reminder to send to a user
    in a Discord text channel (Guild or DM) at a later date
    in time.

    Attributes
    ----------
    scheduled_time : datetime
        TZ aware datetime at which the reminder is scheduled for sending
    created_at : datetime
        TZ aware datetime at which the reminder was created
    context_id : int
        The ID of the context in which the reminder was created,
        either the channel ID of the text channel in which the
        reminder was created, or the user ID of the user who
        created the reminder.
    author_id : int
        The ID of the user who created the reminder.
    guild_id : int
        The ID of the guild in which the reminder was created,
        if applicable.
    note : str
        The message to send to the user when the reminder is sent.
    jump_url : str
        The URL to the message to send to the user when the reminder
        is sent, pointing to the original message invoking the command,
        if applicable.
    _id : ObjectId
        The ID of the reminder in MongoDB, if applicable.
        only used when creating a Reminder from a MongoDB document.
    """

    scheduled_time: datetime
    created_at: datetime
    context_id: int
    author_id: int
    guild_id: int = None
    note: str = None
    jump_url: str = None
    _id: ObjectId = None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Reminder from a MongoDB document.
        """
        reminder = cls(**data)

        # if the datetimes are naive, make them aware (UTC)
        if reminder.scheduled_time.tzinfo is None:
            reminder.scheduled_time = reminder.scheduled_time.replace(
                tzinfo=timezone.utc
            )
        if reminder.created_at.tzinfo is None:
            reminder.created_at = reminder.created_at.replace(
                tzinfo=timezone.utc
            )
        return reminder

    @classmethod
    def from_relative_time_and_ctx(
        cls,
        relative_time: str,
        ctx: BaseContext,
        tz: tzinfo,
        note: str = None,
    ):
        """
        Create a Reminder from a relative time string.
        """
        # Parse relative time
        offset = TimeLength(relative_time)
        delta = timedelta(seconds=offset.total_seconds)

        scheduled_time = datetime.now(tz=tz) + delta

        if not delta:
            raise ValueError(f"Could not parse relative time `{relative_time}`")

        # If the reminder was invoked from a context menu,
        # use the original message's jump URL
        # If the reminder was invoked using a prefixed command,
        # we can use that message.
        # Otherwise, we don't have a jump URL.
        if isinstance(ctx, ContextMenuContext):
            message = ctx.target
            jump_url = message.jump_url

        elif isinstance(ctx, HybridContext) and ctx._message:
            jump_url = ctx._message.jump_url

        elif isinstance(ctx, PrefixedContext):
            jump_url = ctx._message.jump_url

        else:
            jump_url = None

        return cls(
            scheduled_time=scheduled_time,
            created_at=datetime.now(tz=tz),
            context_id=context_id(ctx),
            author_id=ctx.author_id,
            guild_id=ctx.guild_id,
            note=note,
            jump_url=jump_url,
        )

    @property
    def expired(self) -> bool:
        """
        Whether the reminder has expired.
        """
        return self.scheduled_time < datetime.now(tz=timezone.utc)

    @property
    def timestamp(self) -> Timestamp:
        """
        The timestamp of the reminder.
        """
        return Timestamp.fromdatetime(self.scheduled_time)

    @property
    def naive_scheduled_time(self) -> datetime:
        """
        The scheduled time of the reminder, without timezone information,
        localized to the system's timezone.

        Used for setting up the reminder task in interactions.py
        (which only accepts naive datetimes)
        """
        return self.scheduled_time.astimezone(tzlocal()).replace(tzinfo=None)

    @property
    def reply_id(self) -> int | None:
        if self.jump_url is None:
            return None
        return int(self.jump_url.split("/")[-1])

    def to_dict(self) -> dict:
        """
        Convert the Reminder to a dictionary.
        """
        result = asdict(self)
        del result[
            "_id"
        ]  # Remove the _id field to avoid errors when inserting into MongoDB

        return result
