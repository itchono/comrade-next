import pytest
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    CapturingContext,
    fetch_latest_message,
    wait_for_message_or_fetch,
)
from comrade.modules.booru_cmds import Booru


@pytest.fixture(scope="module")
async def booru_ext(bot: Comrade) -> Booru:
    return bot.get_ext("Booru")


@pytest.mark.bot
async def test_booru_start_gelbooru_single(
    capturing_ctx: CapturingContext, booru_ext: Booru
):
    booru_cmd = booru_ext.booru

    await booru_cmd.callback(capturing_ctx, "gelbooru", "id:8435932")

    # Get latest message in channel
    embed_msg = capturing_ctx.testing_captured_message

    embed = embed_msg.embeds[0]

    # TODO: image url not showing up, I think this is a discord bug
    assert embed.title == "id:8435932"
    assert (
        embed.footer.text
        == "Site: Gelbooru | Page 1 | Post 1 | Type 'next' to advance"
    )


@pytest.mark.bot
async def test_booru_advance_msg(ctx: PrefixedContext):
    # starting from the previous test

    # The post list should be depleted now
    await ctx.send("next")

    def check(m: MessageCreate):
        return m.message.author == ctx.bot.user and m.message.content != "next"

    msg = await wait_for_message_or_fetch(ctx, check, timeout=10)

    assert msg.content == "No more results found."

    # This should return no response, because the session is over
    await ctx.send("next")

    # if we try to pull a message, it should only be the last one
    msg_2 = await fetch_latest_message(ctx)
    assert msg_2.content == "next"


@pytest.mark.bot
async def test_booru_start_danbooru_single(
    capturing_ctx: CapturingContext, booru_ext: Booru
):
    booru_cmd = booru_ext.booru

    await booru_cmd.callback(capturing_ctx, "danbooru", "id:6223033")

    # Get latest message in channel
    embed_msg = capturing_ctx.testing_captured_message

    embed = embed_msg.embeds[0]

    # TODO: image url not showing up, I think this is a discord bug
    assert embed.title == "id:6223033"
    assert (
        embed.footer.text
        == "Site: Danbooru | Page 1 | Post 1 | Type 'next' to advance"
    )


@pytest.mark.bot
async def test_booru_advance_callback(
    capturing_ctx: CapturingContext, booru_ext: Booru
):
    # Try advancing using callback
    await booru_ext.booru_next_callback(capturing_ctx)

    msg = capturing_ctx.testing_captured_message
    assert msg.content == "No more results found."

    await booru_ext.booru_next_callback(capturing_ctx)

    err_msg = capturing_ctx.testing_captured_message
    assert "This button was probably created in the past" in err_msg.content


@pytest.mark.bot
async def test_booru_gelbooru_multi(
    capturing_ctx: CapturingContext, booru_ext: Booru
):
    booru_cmd = booru_ext.booru

    await booru_cmd.callback(capturing_ctx, "gelbooru", "tsushima_yoshiko")

    # Advance to the next page and make sure we have a post
    await booru_ext.booru_next_callback(capturing_ctx)

    embed_msg = capturing_ctx.testing_captured_message
    embed = embed_msg.embeds[0]
    assert (
        embed.footer.text
        == "Site: Gelbooru | Page 1 | Post 2 | Type 'next' to advance"
    )


@pytest.mark.bot
async def test_autocomplete_gelbooru_nominal(
    ctx: PrefixedContext,
    booru_ext: Booru,
    monkeypatch: pytest.MonkeyPatch,
):
    tags = []

    # capture the tags that are sent
    async def monkeypatched_send(*args, **kwargs):
        tags.append(args[0])

    with monkeypatch.context() as m:
        m.setattr(
            ctx,
            "kwargs",
            {"booru_name": "gelbooru", "tags": "tsushima_"},
        )
        m.setattr(ctx, "send", monkeypatched_send)

        # execute the autocomplete request
        await booru_ext.tags_autocomplete(ctx)

        # check
        suggestions = tags[0]

        assert "tsushima_yoshiko" in suggestions
        assert "tsushima_(kancolle)" in suggestions


@pytest.mark.bot
async def test_autocomplete_blank(
    ctx: PrefixedContext,
    booru_ext: Booru,
    monkeypatch: pytest.MonkeyPatch,
):
    tags = []

    # capture the tags that are sent
    async def monkeypatched_send(*args, **kwargs):
        tags.append(args[0])

    with monkeypatch.context() as m:
        m.setattr(ctx, "kwargs", {"booru_name": "gelbooru", "tags": ""})
        m.setattr(ctx, "send", monkeypatched_send)

        # execute the autocomplete request
        await booru_ext.tags_autocomplete(ctx)

        # check
        suggestions = tags[0]

        assert suggestions == ["(Start typing to get tag suggestions)"]


@pytest.mark.bot
async def test_autocomplete_no_suggestion(
    ctx: PrefixedContext,
    booru_ext: Booru,
    monkeypatch: pytest.MonkeyPatch,
):
    tags = []

    # capture the tags that are sent
    async def monkeypatched_send(*args, **kwargs):
        tags.append(args[0])

    with monkeypatch.context() as m:
        m.setattr(
            ctx,
            "kwargs",
            {"booru_name": "gelbooru", "tags": "qwertyuiopasdfghjklzxcvbnm"},
        )
        m.setattr(ctx, "send", monkeypatched_send)

        # execute the autocomplete request
        await booru_ext.tags_autocomplete(ctx)

        # check
        suggestions = tags[0]

        assert suggestions == ["qwertyuiopasdfghjklzxcvbnm"]
