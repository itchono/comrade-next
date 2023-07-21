import pytest
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    CapturingContext,
    wait_for_message_or_fetch,
)
from comrade.modules.nhentai_cmds import NHentai


@pytest.fixture(scope="module")
async def nhentai_ext(bot: Comrade) -> NHentai:
    return bot.get_ext("NHentai")


@pytest.mark.bot
async def test_gallery_start(
    offline_ctx: CapturingContext, nhentai_ext: NHentai
):
    nhentai_gallery_cmd = nhentai_ext.nhentai_gallery

    await nhentai_gallery_cmd.callback(offline_ctx, 266745)

    # Get latest message in channel
    start_embed_msg = offline_ctx.captured_message
    assert (
        start_embed_msg.content
        == "Type `np` (or click the buttons) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "Upload duplicate, replace with white page"
    assert start_embed.url == "https://nhentai.net/g/266745/"
    assert (
        start_embed.image.url
        == "https://t.nhentai.net/galleries/1385285/cover.jpg"
    )
    assert start_embed.footer.text == "Found using nhentai.to Mirror"


@pytest.mark.bot
async def test_gallery_next_page_from_init(prefixed_ctx: PrefixedContext):
    """
    Test continuity of gallery pages.
    Has to be executed after test_gallery_start.

    Uses message response
    """
    await prefixed_ctx.send("np")

    def check(m: MessageCreate):
        return (
            m.message.author == prefixed_ctx.bot.user
            and m.message.embeds
            and m.message.channel == prefixed_ctx.channel
        )

    msg = await wait_for_message_or_fetch(prefixed_ctx, check, timeout=10)

    embed = msg.embeds[0]

    assert (
        embed.footer.text
        == "Page 1 of 1 | Upload duplicate, replace with white page (266745)"
    )
    assert embed.image.url is not None


@pytest.mark.bot
async def test_gallery_end(
    capturing_ctx: CapturingContext, nhentai_ext: NHentai
):
    """
    Test that gallery terminates when we reach the end.

    Uses message response, as well as direct button callback.
    """
    await capturing_ctx.send("np")

    def check(m: MessageCreate):
        return (
            m.message.author == capturing_ctx.bot.user
            and not m.message.embeds
            and m.message.content != "np"
            and m.message.channel == capturing_ctx.channel
        )

    msg = await wait_for_message_or_fetch(capturing_ctx, check, timeout=10)

    assert msg.content == "You have reached the end of this work."

    # Now try to go to next page, make sure it doesn't work
    await nhentai_ext.nhentai_np_callback.callback(capturing_ctx)

    msg = capturing_ctx.captured_message

    assert (
        msg.content
        == "This button was probably created in the past, and its session"
        " has expired. Please start a new NHentai session."
    )
