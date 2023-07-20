import asyncio
import logging
import os
import subprocess
from types import SimpleNamespace

import pytest
from interactions import Client, Embed, Guild, GuildText, Message
from pymongo.database import Database

from comrade.core.comrade_client import Comrade
from comrade.core.relay_system import Relay
from comrade.core.relay_system.relay_main import __name__ as logger_name
from comrade.core.relay_system.update_hook import (
    is_valid_update_wh,
    perform_update,
)
from comrade.lib.testing_utils import (
    SAMPLE_MESSAGE_DATA,
    fake_subproc_check_output,
)


@pytest.mark.bot
async def test_relay_init(
    bot: Comrade,
    temporary_guild: Guild,
    mongodb_instance: Database,
    caplog,
):
    """
    Test Relay initialization
    """
    caplog.set_level(logging.INFO, logger=logger_name)

    # ensure the collection is dropped before testing
    mongodb_instance.drop_collection("tempCollection")

    # Create a new relay
    relay = Relay(bot, temporary_guild, mongodb_instance.tempCollection)
    await relay.ensure_channels()

    # Inspect logs to verify that the channels were created
    assert "Created relay channel" in caplog.text

    source_url = "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"

    # Test functionality
    mirrored_doc = await relay.create_blob_from_url(source_url)
    assert mirrored_doc["_id"] == source_url

    # Test that the blob was mirrored
    check_url = await relay.find_blob_by_url(source_url)
    assert check_url == mirrored_doc["blob_url"]

    await asyncio.sleep(1)  # Wait for the message to be sent

    # Ensure the message exists
    msg = await relay.blob_storage_channel.fetch_message(
        mirrored_doc["message_id"]
    )

    assert msg.attachments[0].url == check_url

    # Check cache
    assert source_url in relay.local_cache

    # Test deletion
    await relay.delete_blob(source_url, keep_message=False)

    await asyncio.sleep(1)  # Wait for the message to be deleted

    # Ensure the message was deleted
    assert (
        await relay.blob_storage_channel.fetch_message(
            mirrored_doc["message_id"]
        )
        is None
    )

    # Check cache has deleted the blob
    assert source_url not in relay.local_cache


@pytest.mark.bot
async def test_update_hook_perform_update(
    monkeypatch: pytest.MonkeyPatch, bot: Comrade, channel: GuildText
):
    """
    Check that the update hook works
    """
    stored_args = []

    dummy_msg = SimpleNamespace(channel=channel)

    with monkeypatch.context() as m:

        def mock_execv(*args, **kwargs):
            stored_args.append(args)

        async def bot_stop():
            pass

        m.setattr(os, "execv", mock_execv)
        m.setattr(subprocess, "check_output", fake_subproc_check_output)

        # IMPORTANT: PREVENT THE BOT FROM ACTUALLY STOPPING
        m.setattr(bot, "stop", bot_stop)

        await perform_update(dummy_msg, bot)

        assert "--notify_channel" in stored_args[0][1]


def test_update_hook_filter_nominal():
    message_data = SAMPLE_MESSAGE_DATA()

    message_data["webhook_id"] = 1234567890
    message = Message.from_dict(message_data, Client())

    embed = Embed("[itchono/comrade-next] New tag created: v0.19.1")
    embed.set_author(name="itchono")

    message.embeds = [embed]

    assert is_valid_update_wh(message)


def test_update_hook_filter_invalid_1():
    """
    Invalid because a new tag was not created
    """
    message_data = SAMPLE_MESSAGE_DATA()

    message_data["webhook_id"] = 1234567890
    message = Message.from_dict(message_data, Client())

    embed = Embed("[itchono/comrade-next] New branch created: soundboard_mvp")
    embed.set_author(name="itchono")

    message.embeds = [embed]

    assert not is_valid_update_wh(message)


def test_update_hook_filter_invalid_2():
    """
    Invalid because not a webhook message
    """
    message_data = SAMPLE_MESSAGE_DATA()
    message = Message.from_dict(message_data, Client())

    assert not is_valid_update_wh(message)


def test_update_hook_filter_invalid_3():
    """
    Invalid because no embeds
    """
    message_data = SAMPLE_MESSAGE_DATA()

    message_data["webhook_id"] = 1234567890
    message = Message.from_dict(message_data, Client())

    assert not is_valid_update_wh(message)
