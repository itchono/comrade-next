import pytest
from interactions import BaseContext

from comrade.modules.telemetry import Telemetry


@pytest.mark.bot
async def test_status_cmd(ctx: BaseContext):
    telemetry_ext: Telemetry = ctx.bot.get_ext("Telemetry")

    await telemetry_ext.status.callback(ctx)

    # Get latest message in channel
    embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert embed_msg.embeds[0].title == "Bot Status"
