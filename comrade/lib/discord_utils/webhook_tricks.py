# Send messages using webhooks as different users

from logging import getLogger
from typing import Optional

from interactions import (
    GuildText,
    Member,
    Message,
    Webhook,
    errors,
    logger_name,
)

_logger = getLogger(logger_name)


async def get_channel_webhook(channel: GuildText) -> Webhook:
    """
    Returns Comrade's webhook for the channel, creating one if it does not exist.

    Parameters
    ----------
    channel: interactions.GuildText
        The channel to check.

    Returns
    -------
    interactions.Webhook
        The webhook for the channel.
    """
    # the webhook needs to be owned by the bot
    try:
        valid_webhooks = list(
            filter(
                lambda w: w.user_id == channel.guild.me.id,
                await channel.fetch_webhooks(),
            )
        )
    except errors.Forbidden:
        raise RuntimeError(
            f"Missing permissions to fetch webhooks in {channel.name}"
        )

    if not valid_webhooks:
        _logger.warning(f"Creating webhook in {channel.name}")
        return await channel.create_webhook(name="Comrade")
    else:
        return valid_webhooks[0]


async def send_channel_webhook(
    channel: GuildText, username: str, avatar_url: str, **kwargs
) -> Message:
    """
    Send a message as a webhook using a different username and avatar.

    Parameters
    ----------
    channel: interactions.GuildText
        The channel to send the message in.
    username: str
        The username of the webhook.
    avatar_url: str
        The avatar of the webhook.

    (As well as the parameters for `interactions.Webhook.send`)

    Returns
    -------
    interactions.Message
        The message sent.
    """
    webhook = await get_channel_webhook(channel)

    return await webhook.send(
        username=username, avatar_url=avatar_url, **kwargs
    )


async def echo(
    channel: GuildText,
    member: Member,
    **kwargs,
) -> Optional[Message]:
    """
    Sends a message as the member in the channel.

    Parameters
    ----------
    channel: interactions.GuildText
        The channel to send the message in.
    member: interactions.Member
        The member to mimic.

    (As well as the parameters for `interactions.Webhook.send`)
    """

    return await send_channel_webhook(
        channel,
        username=member.display_name,
        avatar_url=member.avatar.url,
        **kwargs,
    )
