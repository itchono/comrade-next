import logging

import pytest
from aiohttp import ClientSession
from interactions import Client, Guild, logger_name
from pymongo.database import Database

from comrade.core.relay import Relay


@pytest.fixture(scope="session")
async def blank_guild(generic_bot: Client) -> Guild:
    """
    Create a blank guild, which is cleaned up after the test
    """
    guild = await Guild.create("Comrade Test Guild Temp", generic_bot)
    yield guild
    await guild.delete()


@pytest.mark.bot
async def test_relay_init(
    blank_guild: Guild,
    caplog,
    http_session: ClientSession,
    mongodb_instance: Database,
):
    """
    Test Relay initialization
    """
    caplog.set_level(logging.INFO, logger=logger_name)

    # Create a new relay
    relay = Relay(blank_guild, http_session, mongodb_instance.relayBlobs)
    await relay.ensure_channels()

    # Inspect logs to verify that the channels were created
    assert "Created relay channel" in caplog.text

    source_url = "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"

    # Test functionality
    mirrored_url = await relay.mirror_blob(source_url)
    assert mirrored_url is not None

    # Test that the blob was mirrored
    doc = mongodb_instance.relayBlobs.find_one({"blob_url": mirrored_url})
    assert doc["source_url"] == source_url

    # Clean up
    mongodb_instance.relayBlobs.delete_one({"blob_url": mirrored_url})
