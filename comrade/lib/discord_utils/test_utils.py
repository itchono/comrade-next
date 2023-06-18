# Taken from interactions.py tests folder
from typing import Optional

import discord_typings
from interactions import Client, Message, Snowflake_Type
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

    return PrefixedContext.from_message(
        client, Message.from_dict(message, client)
    )
