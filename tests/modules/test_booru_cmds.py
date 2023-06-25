import asyncio

import pytest
from interactions import BaseContext, InteractionCommand
from interactions.api.events import MessageCreate

from comrade.core.configuration import TEST_GUILD_ID


@pytest.mark.bot
async def test_booru_start_gelbooru(ctx: BaseContext):
    booru_cmd: InteractionCommand = ctx.bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["booru"]

    await booru_cmd.callback(ctx, "gelbooru", "id:8435932")

    # Get latest message in channel
    embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    embed = embed_msg.embeds[0]

    # TODO: image url not showing up, I think this is a discord bug
    assert embed.title == "id:8435932"
    assert (
        embed.footer.text
        == "Site: Gelbooru | Page 1 | Post 1 | Type 'next' to advance"
    )

    # The post list should be depleted now
    await ctx.send("next")

    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create",
        checks=lambda m: m.message.author == ctx.bot.user,
        timeout=5,
    )

    assert msg_event.message.content == "No more results found."

    # This should return no response, because the session is over
    await ctx.send("next")

    with pytest.raises(asyncio.TimeoutError):
        await ctx.bot.wait_for(
            "message_create",
            checks=lambda m: m.message.author == ctx.bot.user,
            timeout=1,
        )
