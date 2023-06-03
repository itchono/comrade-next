from interactions import BaseContext


def nsfw_channel(ctx: BaseContext) -> bool:
    """
    Returns True if the command is being used in an NSFW channel,
    or if the command is being used in a DM.
    """
    if ctx.guild is None:
        return True

    return ctx.channel.nsfw


def is_owner(ctx: BaseContext) -> bool:
    """
    Returns True if the command is being used by the bot owner.
    """
    return ctx.author.id in ctx.bot.owner_ids
