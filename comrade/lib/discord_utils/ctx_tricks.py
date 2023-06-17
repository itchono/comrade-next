from collections import UserDict
from typing import TypeVar

from interactions import BaseContext, Client, GuildText, Snowflake, User

# Type variable for values in ContextDict
_VT = TypeVar("_VT")


def context_id(ctx: BaseContext) -> Snowflake:
    """
    Unique identifier for a given context's channel
    which works for both guild and DM channels

    Parameters
    ----------
    ctx : BaseContext
        The context to get the id from.

    Returns
    -------
    Snowflake
        Either the channel_id if the context is in a guild,
        or the author_id if the context is in a DM.
    """
    if ctx.guild_id:
        return ctx.channel_id
    return ctx.author_id


class ContextDict(UserDict[BaseContext, _VT]):
    """
    Dictionary subclass whose keys
    are derived from BaseContext instances.

    Converts the context to a unique identifier
    per-channel, useful for caching results or sessions
    in guild channels and DMs.
    """

    def __setitem__(self, key: BaseContext, value: _VT):
        return super().__setitem__(context_id(key), value)

    def __getitem__(self, key: BaseContext) -> _VT:
        return super().__getitem__(context_id(key))


async def messageable_from_context_id(
    context_id: Snowflake, bot: Client
) -> GuildText | User:
    """
    Performs the "reverse" of context_id(),
    gives the Guild Text channel or User from which
    the context_id was generated.

    Parameters
    ----------
    context_id : Snowflake
        The context ID to get the messageable from.
    bot : Client
        The bot instance to use to get the messageable.

    Returns
    -------
    GuildText | User
        The messageable from which the context ID was generated.

    Raises
    ------
    ValueError
        If the context ID does not correspond to a valid
        Guild Text channel or User.
    """
    if channel := bot.get_channel(context_id):
        return channel
    elif user := bot.get_user(context_id):
        return user

    raise ValueError(
        f"Context ID `{context_id}` does not correspond"
        " to a valid Guild Text channel or User."
    )
