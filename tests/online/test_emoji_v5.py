import asyncio

import pytest
from interactions import BaseContext
from interactions.api.events import MessageCreate

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import TEST_MODE

if not TEST_MODE:
    pytest.skip("Skipping online tests", allow_module_level=True)


async def test_sending_emoji(bot: Comrade, ctx: BaseContext):
    await ctx.send(":pssh:")

    def check(m: MessageCreate):
        return m.message.webhook_id is not None

    # Wait for bot to send message
    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create", checks=check, timeout=5
    )

    emoji_msg = msg_event.message
    assert (
        emoji_msg.content
        == "https://cdn.discordapp.com/attachments/810726667026300958/810732433460559872/pssh.png"
    )
