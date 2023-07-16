import pytest

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    CapturingContext,
)
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_gallery_start(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    nhentai_gallery_cmd = nhentai_ext.nhentai_gallery

    await nhentai_gallery_cmd.callback(capturing_ctx, 185217)

    # Get latest message in channel
    start_embed_msg = capturing_ctx.testing_captured_message
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "R.E.I.N.A"
    assert start_embed.url == "https://nhentai.net/g/185217/"
    assert (
        start_embed.image.url
        == "https://t.nhentai.net/galleries/1019423/cover.jpg"
    )
    assert start_embed.footer.text == "Found using nhentai.to Mirror"


@pytest.mark.bot
async def test_gallery_next_page_from_init(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Test continuity of gallery pages.
    Has to be executed after test_gallery_start.

    Uses the button callback directly.
    """
    await nhentai_ext.nhentai_np_callback.callback(capturing_ctx)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 1 of 28 | R.E.I.N.A (185217)"
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_prev_page_from_first(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "previous page" button on the first page
    does not do anything.
    """
    await nhentai_ext.nhentai_pp_callback.callback(capturing_ctx)

    msg = capturing_ctx.testing_captured_message
    assert msg.content == "You are at the beginning of this work."


@pytest.mark.bot
async def test_gallery_next_page_from_first(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "next page" button on the first page
    correctly advances the gallery.
    """
    await nhentai_ext.nhentai_np_callback.callback(capturing_ctx)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 2 of 28 | R.E.I.N.A (185217)"
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_jump_page_nominal(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Test that we can skip to any page.
    """
    await nhentai_ext.nhentai_gpage.callback(capturing_ctx, 10)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 10 of 28 | R.E.I.N.A (185217)"
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_jump_page_too_far(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Test that we cannot skip to a page that does not exist.
    """
    await nhentai_ext.nhentai_gpage.callback(capturing_ctx, 29)

    msg = capturing_ctx.testing_captured_message

    assert msg.content == "Invalid page number. Must be between 1 and 28."


@pytest.mark.bot
async def test_gallery_prev_page_from_middle(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "previous page" button on the last page
    correctly goes back a page.
    """
    # skip to last page
    await nhentai_ext.nhentai_gpage.callback(capturing_ctx, 15)

    await nhentai_ext.nhentai_pp_callback.callback(capturing_ctx)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 14 of 28 | R.E.I.N.A (185217)"
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_prev_page_from_end(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Tests that pressing the "previous page" button on the last page
    correctly goes back a page.
    """
    # skip to last page
    await nhentai_ext.nhentai_gpage.callback(capturing_ctx, 28)

    await nhentai_ext.nhentai_pp_callback.callback(capturing_ctx)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]

    assert embed.footer.text == "Page 27 of 28 | R.E.I.N.A (185217)"
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_end(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Test that gallery terminates when we reach the end.
    """

    # skip to last page
    await nhentai_ext.nhentai_gpage.callback(capturing_ctx, 28)

    # try to advance
    await nhentai_ext.nhentai_np_callback.callback(capturing_ctx)

    msg_1 = capturing_ctx.testing_captured_message

    assert msg_1.content == "You have reached the end of this work."

    # try to keep going
    await nhentai_ext.nhentai_np_callback.callback(capturing_ctx)
    msg_2 = capturing_ctx.testing_captured_message
    assert (
        msg_2.content == "This button was probably created in the past, "
        "and its session has expired. Please start a new NHentai session."
    )
