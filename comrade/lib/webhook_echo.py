# Send messages using webhooks as different users


from typing import List, Optional, Union

from interactions import (
    BaseComponent,
    Embed,
    GuildText,
    Member,
    Message,
    Webhook,
    errors,
)


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
        valid_webhooks = filter(
            lambda w: w.user == channel.guild.me, await channel.fetch_webhooks()
        )
    except errors.Forbidden:
        # Put an error msg TODO
        return None

    if not valid_webhooks:
        return await channel.create_webhook(name="Comrade")
    else:
        return next(valid_webhooks)


async def send_mimic(
    channel: GuildText,
    content: str = None,
    username: str = None,
    avatar_url: str = None,
    embed: Optional[Union["Embed", dict]] = None,
    embeds: Optional[
        Union[List[Union["Embed", dict]], Union["Embed", dict]]
    ] = None,
    components: Optional[
        Union[
            List[List[Union["BaseComponent", dict]]],
            List[Union["BaseComponent", dict]],
            "BaseComponent",
            dict,
        ]
    ] = None,
    **kwargs,
) -> Optional[Message]:
    """
    Send a message as a webhook using a different username and avatar.

    Parameters
    ----------
    channel: interactions.GuildText
        The channel to send the message in.
    content: str, optional
        The content of the message.
    username: str, optional
        The username of the webhook.
    avatar_url: str, optional
        The avatar of the webhook.
    embed: interactions.Embed, optional
        The embed to send.
    embeds: list[interactions.Embed], optional
        The embeds to send.
    components: list[list[interactions.BaseComponent]], optional
        The components to send.

    Notes
    -----
    Falls back to sending a normal message if the bot cannot find a webhook.

    """
    webhook = await get_channel_webhook(channel)

    if webhook is None:
        return channel.send(
            content=content,
            embed=embed,
            embeds=embeds,
            components=components,
            **kwargs,
        )

    return await webhook.send(
        content=content,
        username=username,
        avatar_url=avatar_url,
        embed=embed,
        embeds=embeds,
        components=components,
        **kwargs,
    )


async def echo(
    channel: GuildText,
    member: Member,
    content: str = None,
    embed: Optional[Union["Embed", dict]] = None,
    embeds: Optional[
        Union[List[Union["Embed", dict]], Union["Embed", dict]]
    ] = None,
    components: Optional[
        Union[
            List[List[Union["BaseComponent", dict]]],
            List[Union["BaseComponent", dict]],
            "BaseComponent",
            dict,
        ]
    ] = None,
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
    content: str, optional
        The content of the message.
    embed: interactions.Embed, optional
        The embed to send.
    embeds: list[interactions.Embed], optional
        The embeds to send.
    components: list[list[interactions.BaseComponent]], optional
        The components to send.

    Notes
    -----
    Falls back to sending a normal message if the bot cannot find a webhook.
    """

    return await send_mimic(
        channel,
        content=content,
        username=member.display_name,
        avatar_url=member.avatar.url,
        embed=embed,
        embeds=embeds,
        components=components,
        **kwargs,
    )
