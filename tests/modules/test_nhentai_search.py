import pytest
from interactions import BaseContext, ComponentType, InteractionCommand
from interactions.api.events import MessageCreate

from comrade.core.configuration import TEST_GUILD_ID


@pytest.mark.bot
async def test_search_start(ctx: BaseContext):
    nhentai_search_cmd: InteractionCommand = ctx.bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["nhentai search"]

    await nhentai_search_cmd.callback(ctx, "alp love live english kurosawa")

    def check(event: MessageCreate):
        assert event.message.author.id == ctx.bot.user.id

    start_msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert start_msg.content == "Select a gallery to view (Page 1 / 1)"
    assert start_msg.components[0].type == ComponentType.ACTION_ROW
    assert (
        start_msg.components[0].components[0].type
        == ComponentType.STRING_SELECT
    )
