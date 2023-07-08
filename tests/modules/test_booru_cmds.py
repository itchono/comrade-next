import pytest
from interactions import BaseContext, InteractionCommand
from interactions.api.events import MessageCreate

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.testing_utils import (
    fetch_latest_message,
    wait_for_message_or_fetch,
)


@pytest.mark.bot
async def test_booru_start_gelbooru(ctx: BaseContext):
    booru_cmd: InteractionCommand = ctx.bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["booru"]

    await booru_cmd.callback(ctx, "gelbooru", "id:8435932")

    # Get latest message in channel
    embed_msg = await fetch_latest_message(ctx)

    embed = embed_msg.embeds[0]

    # TODO: image url not showing up, I think this is a discord bug
    assert embed.title == "id:8435932"
    assert (
        embed.footer.text
        == "Site: Gelbooru | Page 1 | Post 1 | Type 'next' to advance"
    )

    # The post list should be depleted now
    await ctx.send("next")

    def check(m: MessageCreate):
        return m.message.author == ctx.bot.user and m.message.content != "next"

    msg = await wait_for_message_or_fetch(ctx, check)

    assert msg.content == "No more results found."

    # This should return no response, because the session is over
    await ctx.send("next")

    # if we try to pull a message, it should only be the last one
    msg_2 = await wait_for_message_or_fetch(ctx, check)
    assert msg_2.content == "next"
