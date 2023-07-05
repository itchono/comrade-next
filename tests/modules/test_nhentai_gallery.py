import pytest
from interactions import BaseContext
from interactions.api.events import MessageCreate

from comrade.core.bot_subclass import Comrade
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_gallery_start(ctx: BaseContext, nhentai_ext: NHentai):
    nhentai_gallery_cmd = nhentai_ext.nhentai_gallery

    await nhentai_gallery_cmd.callback(ctx, 266745)

    # Get latest message in channel
    start_embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "Upload duplicate, replace with white page"
    assert start_embed.url == "https://nhentai.net/g/266745/"
    assert start_embed.footer.text == "Found using nhentai.to Mirror"


@pytest.mark.bot
async def test_gallery_next_page(ctx: BaseContext):
    """
    Test continuity of gallery pages.
    Has to be executed after test_gallery_start.
    """
    await ctx.send("np")

    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create",
        checks=lambda e: e.message.author == ctx.author and e.message.embeds,
    )
    embed = msg_event.message.embeds[0]

    assert (
        embed.footer.text
        == "Page 1 of 1 | Upload duplicate, replace with white page (266745)"
    )
    # assert embed.image.url is not None
    # bugged, pending interactions.py fix

    await ctx.send("np")
    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create", checks=lambda e: e.message.author == ctx.author
    )

    assert msg_event.message.content == "You have reached the end of this work."
