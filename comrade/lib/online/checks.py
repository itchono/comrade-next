from interactions import BaseContext


async def nsfw_channel(ctx: BaseContext) -> bool:
    """
    Returns True if the command is being used in an NSFW channel,
    or if the command is being used in a DM.
    """
    if ctx.guild is None:
        return True

    return ctx.channel.nsfw
