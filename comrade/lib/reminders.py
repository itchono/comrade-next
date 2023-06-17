from dataclasses import asdict, dataclass
from datetime import datetime

from arrow import Arrow
from interactions import BaseContext, ContextMenuContext, Timestamp
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.lib.discord_utils import context_id


@dataclass
class Reminder:
    """
    Representation of a reminder to send to a user
    in a Discord text channel (Guild or DM) at a later date
    in time.

    Attributes
    ----------
    time_utc : datetime
        The UTC time at which the reminder should be sent.
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
    """

    time_utc: datetime
    context_id: int
    author_id: int
    guild_id: int = None
    note: str = None
    jump_url: str = None

    @classmethod
    def from_dict(cls, data: dict):
        """
        Create a Reminder from a MongoDB document.
        """
        del data["_id"]  # Remove the MongoDB ID
        return cls(**data)

    @classmethod
    async def from_relative_time_and_ctx(
        cls,
        relative_time: str,
        ctx: BaseContext,
        note: str = None,
    ):
        """
        Create a Reminder from a relative time string.
        """
        # Convert the relative time to an Arrow time
        # This will automatically raise a ValueError if the time is invalid
        time_from_now = Arrow.dehumanize(Arrow.now(), relative_time)

        # Check that the time is in the future
        if time_from_now < Arrow.now():
            past_timestamp = Timestamp.fromdatetime(time_from_now.naive)
            raise ValueError(
                "Reminder must be in the future. Your reminder "
                f"would have occurred at {past_timestamp.format('F')}."
            )

        # If the reminder was invoked from a context menu,
        # use the original message's jump URL
        # If the reminder was invoked using a prefixed command,
        # we can use that message.
        # Otherwise, we don't have a jump URL.
        if isinstance(ctx, ContextMenuContext):
            channel = await ctx.bot.fetch_channel(ctx.channel_id)
            message = await channel.fetch_message(ctx.target_id)
            jump_url = message.jump_url

        elif isinstance(ctx, PrefixedContext):
            jump_url = ctx._message.jump_url

        else:
            jump_url = None

        return cls(
            time_from_now.naive,
            context_id(ctx),
            ctx.author_id,
            ctx.guild_id,
            note,
            jump_url,
        )

    @property
    def expired(self) -> bool:
        """
        Whether the reminder has expired.
        """
        return self.time_utc < datetime.utcnow()

    @property
    def timestamp(self) -> Timestamp:
        """
        The timestamp of the reminder.
        """
        return Timestamp.fromdatetime(self.time_utc)

    def to_dict(self) -> dict:
        """
        Convert the Reminder to a dictionary.
        """
        return asdict(self)
