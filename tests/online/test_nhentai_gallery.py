import pytest
from interactions import GuildText, InteractionCommand

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import TEST_GUILD_ID, TEST_MODE
from comrade.lib.discord_utils import generate_dummy_context

if not TEST_MODE:
    pytest.skip("Skipping online tests", allow_module_level=True)


async def test_gallery_start(bot: Comrade, channel: GuildText):
    ctx = generate_dummy_context(channel_id=channel.id, client=bot)

    nhentai_gallery_cmd: InteractionCommand = bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["nhentai gallery"]

    await nhentai_gallery_cmd.callback(ctx, 266745)

    # Get latest message in channel
    msgs = await channel.fetch_messages(limit=1)
    msg = msgs[0]

    assert (
        msg.content
        == "Type `np` (or click the button) to start reading, and advance pages."
    )
