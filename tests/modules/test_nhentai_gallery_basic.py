import pytest
from interactions import BaseContext
from interactions.api.events import MessageCreate

from comrade.core.bot_subclass import Comrade
from comrade.lib.testing_utils import (
    fetch_latest_message,
    wait_for_message_or_fetch,
)
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_gallery_start(ctx: BaseContext, nhentai_ext: NHentai):
    nhentai_gallery_cmd = nhentai_ext.nhentai_gallery

    await nhentai_gallery_cmd.callback(ctx, 266745)

    # Get latest message in channel
    start_embed_msg = await fetch_latest_message(ctx)
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "Upload duplicate, replace with white page"
    assert start_embed.url == "https://nhentai.net/g/266745/"
    assert start_embed.footer.text == "Found using nhentai.to Mirror"


@pytest.mark.bot
async def test_gallery_next_page_from_init(ctx: BaseContext):
    """
    Test continuity of gallery pages.
    Has to be executed after test_gallery_start.

    Uses message response
    """
    await ctx.send("np")

    def check(m: MessageCreate):
        return m.message.author == ctx.bot.user and m.message.embeds

    msg = await wait_for_message_or_fetch(ctx, check)

    embed = msg.embeds[0]

    assert (
        embed.footer.text
        == "Page 1 of 1 | Upload duplicate, replace with white page (266745)"
    )
    # assert embed.image.url is not None
    # bugged, pending interactions.py fix


@pytest.mark.bot
async def test_gallery_end(ctx: BaseContext, nhentai_ext: NHentai):
    """
    Test that gallery terminates when we reach the end.

    Uses message response, as well as direct button callback.
    """
    await ctx.send("np")

    def check(m: MessageCreate):
        return (
            m.message.author == ctx.bot.user
            and not m.message.embeds
            and m.message.content != "np"
        )

    msg = await wait_for_message_or_fetch(ctx, check)

    assert msg.content == "You have reached the end of this work."

    # Now try to go to next page, make sure it doesn't work
    await nhentai_ext.nhentai_np_callback.callback(ctx)

    msg = await fetch_latest_message(ctx)

    assert (
        msg.content
        == "This button was probably created in the past, and its session"
        " has expired. Please start a new NHentai session."
    )
