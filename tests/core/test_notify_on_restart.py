import asyncio

import pytest
from interactions import GuildText
from interactions.api.events import MessageCreate

from comrade.core.comrade_client import Comrade
from comrade.core.configuration import BOT_TOKEN


@pytest.mark.bot
async def test_restart_with_notify(bot: Comrade, channel: GuildText):
    """
    Test that the bot sends a notification when it restarts
    """

    # NOTE THAT WE ARE CREATING A NEW BOT INSTANCE
    fresh_bot = Comrade(notify_on_restart=channel.id)

    asyncio.create_task(fresh_bot.login(BOT_TOKEN))
    asyncio.create_task(fresh_bot.start_gateway())

    await fresh_bot.wait_until_ready()

    # EVERYTHING BELOW HERE USES THE EXISTING BOT INSTANCE
    msg_event: MessageCreate = await bot.wait_for(
        "message_create",
        timeout=5,
        checks=lambda m: m.message.author.id == bot.user.id,
    )

    assert msg_event.message.content.startswith(
        "Bot has restarted, current version is"
    )

    # Teardown
    await fresh_bot.stop()
