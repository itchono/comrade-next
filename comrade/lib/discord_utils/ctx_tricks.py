from interactions import ComponentContext, Message, MessageableMixin, Snowflake


def multi_ctx_dispatch(
    msg_ctx: Message | ComponentContext,
) -> tuple[MessageableMixin, Snowflake]:
    """
    Turns a message or component context into a messageable and channel id.

    Parameters
    ----------
    msg_ctx : Message | ComponentContext
        The message or component context to dispatch.

    Returns
    -------
    tuple[MessageableMixin, Snowflake]
        The messageable and channel id.
    """
    if isinstance(msg_ctx, Message):
        return msg_ctx.channel, msg_ctx.channel.id
    else:
        return msg_ctx, msg_ctx.channel_id
