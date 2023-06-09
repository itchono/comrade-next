# Send messages using webhooks as different users


from inspect import Signature, signature
from typing import Callable, Optional, TypeVar

from interactions import GuildText, Member, Message, Webhook, errors

_TFunc = TypeVar("_TFunc", bound=Callable[..., Message])


def patch_signature_to_match_message_send(func: _TFunc) -> _TFunc:
    """
    Patch the signature of a function to match `interactions.Message.send`.
    """

    wh_send_signature = signature(Webhook.send)

    # we can get rid of the first parameter, `self`,
    # as well as `username` and `avatar_url`
    wh_send_params = list(
        filter(
            lambda p: p.name not in ("self", "username", "avatar_url"),
            wh_send_signature.parameters.values(),
        )
    )

    # get signature of func, removing **kwargs
    func_signature = signature(func)
    func_params = list(func_signature.parameters.values())[:-1]

    new_signature = Signature(func_params + wh_send_params)
    func.__signature__ = new_signature

    return func


def patch_annotation(func: _TFunc) -> _TFunc:
    """
    Patch the docstring and annotations of a function to match
    `interactions.Message.send`, similar to `patch_signature_to_match_message_send`.
    """

    wh_send_annotations = Webhook.send.__annotations__

    for key in ["return", "self", "username", "avatar_url"]:
        wh_send_annotations.pop(key, None)

    func.__annotations__.update(wh_send_annotations)

    return func


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
        raise RuntimeError(
            f"Missing permissions to fetch webhooks in {channel.name}"
        )

    if not valid_webhooks:
        return await channel.create_webhook(name="Comrade")
    else:
        return next(valid_webhooks)


@patch_annotation
@patch_signature_to_match_message_send
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


@patch_annotation
@patch_signature_to_match_message_send
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
