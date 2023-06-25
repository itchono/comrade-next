import asyncio
import logging

import pytest
from interactions import Guild, logger_name
from pymongo.database import Database

from comrade.core.bot_subclass import Comrade
from comrade.core.relay import Relay


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

    # Create a new relay
    relay = Relay(bot, temporary_guild, mongodb_instance.blobStorage)
    await relay.ensure_channels()

    # Inspect logs to verify that the channels were created
    assert "Created relay channel" in caplog.text

    source_url = "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"

    # Test functionality
    mirrored_doc = await relay.create_blob_from_url(source_url)
    assert mirrored_doc["_id"] == source_url

    # Test that the blob was mirrored
    check_url = await relay.find_blob_url(source_url)
    assert check_url == mirrored_doc["blob_url"]

    await asyncio.sleep(1)  # Wait for the message to be sent

    # Ensure the message exists
    msg = await relay.blob_storage_channel.fetch_message(
        mirrored_doc["message_id"]
    )

    assert msg.attachments[0].url == check_url

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
