# Taken from interactions.py tests folder
import asyncio
from typing import Callable, Optional

import discord_typings
from interactions import BaseContext, Client, Message, Snowflake_Type
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext
from interactions.models.internal.context import InteractionContext


def SAMPLE_USER_DATA(user_id: Optional[str] = None) -> discord_typings.UserData:
    if user_id is None:
        user_id = "123456789012345678"

    return {
        "id": user_id,
        "username": "test_user",
        "discriminator": "1234",
        "avatar": "",
    }


def SAMPLE_MESSAGE_DATA(
    channel_id: Optional[str] = None,
    user_id: Optional[str] = None,
    message_id: Optional[str] = None,
    guild_id: Optional[str] = None,
) -> discord_typings.MessageCreateData:
    if channel_id is None:
        channel_id = "123456789012345678"
    if message_id is None:
        message_id = "123456789012345677"
    data = {
        "id": message_id,
        "channel_id": channel_id,
        "author": SAMPLE_USER_DATA(user_id),
        "content": "test_message",
        "timestamp": "2022-07-16T20:56:55.999419+01:00",
        "edited_timestamp": None,
        "tts": False,
        "mention_everyone": False,
        "mentions": [SAMPLE_USER_DATA(user_id)],
        "mention_roles": [],
        "mention_channels": [],
        "attachments": [],
        "embeds": [],
        "reactions": [],
        "nonce": None,
        "pinned": False,
        "webhook_id": None,
        "type": 0,
        "activity": None,
        "application": None,
        "application_id": None,
        "message_reference": None,
        "flags": 0,
        "refereces_message": None,
        # "interaction": None,
        "thread": None,
        "components": [],
        "sticker_items": [],
    }
    if guild_id is not None:
        data["guild_id"] = guild_id
    return data


def generate_dummy_context(
    user_id: Snowflake_Type | None = None,
    channel_id: Snowflake_Type | None = None,
    guild_id: Snowflake_Type | None = None,
    message_id: Snowflake_Type | None = None,
    dm: bool = False,
    client: Client | None = None,
) -> InteractionContext:
    """Generates a dummy context for testing."""
    client = Client() if client is None else client

    if not dm and not guild_id:
        guild_id = "123456789012345670"
    elif dm:
        guild_id = None

    # channel = SAMPLE_CHANNEL_DATA(channel_id=channel_id, guild_id=guild_id)
    message = SAMPLE_MESSAGE_DATA(
        user_id=user_id,
        channel_id=channel_id,
        message_id=message_id,
        guild_id=guild_id,
    )

    ctx = PrefixedContext.from_message(
        client, Message.from_dict(message, client)
    )

    # Monkeypatch a .defer coroutine to the context
    async def defer():
        pass

    ctx.defer = defer

    return ctx


async def fetch_latest_message(ctx: BaseContext) -> Message:
    """Fetch the latest message in the channel."""
    return (await ctx.channel.fetch_messages(limit=1))[0]


async def wait_for_message_or_fetch(
    ctx: BaseContext,
    check: Callable[[MessageCreate], bool],
    timeout: Optional[float] = 3,
) -> Message:
    """
    Wait for a message to be sent in the channel, or fetch the last message
    if it has already been sent.

    Useful for testing commands that send messages.

    Parameters
    ----------
    ctx : BaseContext
        The context to wait for a message in
    check : Callable[[MessageCreate], bool]
        The check to use for the wait_for
    timeout : Optional[float]
        The timeout for the wait_for, defaults to 3 seconds
        set it longer to allow for slow CI (ratelimits)

    Returns
    -------
    Message
        The message that was sent
    """
    try:
        # Wait for bot to send message
        msg_event: MessageCreate = await ctx.bot.wait_for(
            "message_create", checks=check, timeout=timeout
        )
        return msg_event.message
    except asyncio.TimeoutError:
        # If the bot has already sent the message and we couldn't see the event
        # fetch the latest message
        return await fetch_latest_message(ctx)


def fake_subproc_check_output(*args, **kwargs) -> str:
    """
    Monkeypatched subprocess.check, used to spoof output
    from git and pip commands.
    """
    ex_args = args[0]

    match ex_args:
        case ["git", "branch", "--show-current"]:
            return "main"
        case ["git", "rev-parse", "--short", "HEAD"]:
            return "1234567"
        case ["git", "fetch"]:
            return ""
        case ["git", "pull"]:
            return "Already up to date."
        case ["git", "status"]:
            return (
                "On branch main\nYour branch is up to date "
                "with 'origin/main'.\n\nnothing to commit, working tree clean"
            )
        case [*_, "-m", "pip", "install", "-e", ".", "--upgrade"]:
            return "Successfully installed comrade"

        case _:
            return ""


class CapturingContext(PrefixedContext):
    """
    Added functions for performing:
    1. capturing of messages sent by the bot
    2. bypassing of internet requests for sending messages

    This is created by pytest fixtures and monkeypatching
    """

    testing_captured_message: Message

    async def send_and_capture(self, *args, **kwargs) -> Message:
        self.testing_captured_message = await PrefixedContext.send(
            self, *args, **kwargs
        )
        return self.testing_captured_message

    async def fake_send_http_request(self, *args, **kwargs):
        """
        For use with monkeypatching; bypasses the internet
        and instead plugs in a fake response.
        """
        # Extract message payload fields, and patch in any missing ones
        msg_payload: dict = SAMPLE_MESSAGE_DATA(user_id=self.bot.user.id)
        msg_payload.update(args[0])

        self.testing_captured_message = Message.from_dict(
            msg_payload, self.client
        )
        return None
