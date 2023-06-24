import pytest
from interactions import Guild

from comrade.core.bot_subclass import Comrade
from comrade.lib.relay import Relay


@pytest.mark.bot
async def test_relay_init(bot: Comrade):
    """
    Test Relay initialization
    """

    # Create a new guild
    blank_guild = await Guild.create("test_relay_init", bot)

    # Create a new relay
    relay = Relay(blank_guild, bot.http_session, bot.db.relayBlobs)
    await relay.ensure_channels()

    # Ensure that the channels exist
    url = await relay.mirror_blob(
        "https://img3.gelbooru.com/images/ee/3a/ee3a33cc0cf29e9956f2c2f5a35d6ca8.png"
    )
    assert url is not None

    await blank_guild.delete()
