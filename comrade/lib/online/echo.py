# Send messages using webhooks as different users

import interactions


async def get_channel_webhook(channel: interactions.GuildText) -> interactions.Webhook:
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
        valid_webhooks = filter(
            lambda w: w.user == channel.guild.me, await channel.fetch_webhooks()
        )
    except interactions.errors.Forbidden:
        # Put an error msg TODO
        return None

    if not valid_webhooks:
        return await channel.create_webhook(name="Comrade")
    else:
        return next(valid_webhooks)
