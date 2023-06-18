import asyncio

import pytest
from interactions import BaseContext, InteractionCommand

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import TEST_GUILD_ID, TEST_MODE

if not TEST_MODE:
    pytest.skip("Skipping online tests", allow_module_level=True)


async def test_reminder_from_slash(bot: Comrade, ctx: BaseContext):
    reminder_slash_cmd: InteractionCommand = bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["remind"]

    await reminder_slash_cmd.callback(ctx, "in 6 seconds", "test reminder")

    # Get latest message in channel
    reminder_confirmation_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert reminder_confirmation_msg.content.startswith(
        "Reminder registered to send"
    )

    # await asyncio.sleep(10)

    # # Get latest message in channel
    # reminder_embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    # embed = reminder_embed_msg.embeds[0]
    # assert embed.description == "test reminder"
