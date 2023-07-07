import pytest
from interactions import BaseContext

from comrade.core.bot_subclass import Comrade
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_gallery_start(ctx: BaseContext, nhentai_ext: NHentai):
    nhentai_gallery_cmd = nhentai_ext.nhentai_gallery

    await nhentai_gallery_cmd.callback(ctx, 185217)

    # Get latest message in channel
    start_embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "R.E.I.N.A"
    assert start_embed.url == "https://nhentai.net/g/185217/"
    assert start_embed.footer.text == "Found using nhentai.to Mirror"


@pytest.mark.bot
async def test_gallery_next_page_from_init(
    ctx: BaseContext, nhentai_ext: NHentai
):
    """
    Test continuity of gallery pages.
    Has to be executed after test_gallery_start.

    Uses the button callback directly.
    """
    await nhentai_ext.nhentai_np_callback.callback(ctx)

    embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 1 of 28 | R.E.I.N.A (185217)"
    # assert embed.image.url is not None
    # bugged, pending interactions.py fix


@pytest.mark.bot
async def test_gallery_prev_page_from_first(
    ctx: BaseContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "previous page" button on the first page
    does not do anything.
    """
    await nhentai_ext.nhentai_pp_callback.callback(ctx)

    msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert msg.content == "You are at the beginning of this work."


@pytest.mark.bot
async def test_gallery_next_page_from_first(
    ctx: BaseContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "next page" button on the first page
    correctly advances the gallery.
    """
    await nhentai_ext.nhentai_np_callback.callback(ctx)

    embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 2 of 28 | R.E.I.N.A (185217)"
    # assert embed.image.url is not None
    # bugged, pending interactions.py fix


@pytest.mark.bot
async def test_gallery_jump_page_nominal(
    ctx: BaseContext, nhentai_ext: NHentai
):
    """
    Test that we can skip to any page.
    """
    await nhentai_ext.nhentai_gpage.callback(ctx, 10)

    embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 10 of 28 | R.E.I.N.A (185217)"
    # assert embed.image.url is not None
    # bugged, pending interactions.py fix


@pytest.mark.bot
async def test_gallery_jump_page_too_far(
    ctx: BaseContext, nhentai_ext: NHentai
):
    """
    Test that we cannot skip to a page that does not exist.
    """
    await nhentai_ext.nhentai_gpage.callback(ctx, 29)

    msg = (await ctx.channel.fetch_messages(limit=1))[0]

    assert msg.content == "Invalid page number. Must be between 1 and 28."


@pytest.mark.bot
async def test_gallery_end(ctx: BaseContext, nhentai_ext: NHentai):
    """
    Test that gallery terminates when we reach the end.
    """

    # skip to last page
    await nhentai_ext.nhentai_gpage.callback(ctx, 28)

    # try to advance
    await nhentai_ext.nhentai_np_callback.callback(ctx)

    msg_1 = (await ctx.channel.fetch_messages(limit=1))[0]

    assert msg_1.content == "You have reached the end of this work."

    # try to keep going
    await nhentai_ext.nhentai_np_callback.callback(ctx)
    msg_2 = (await ctx.channel.fetch_messages(limit=1))[0]

    assert (
        msg_2.content == "This button was probably created in the past, "
        "and its session has expired. Please start a new NHentai session."
    )