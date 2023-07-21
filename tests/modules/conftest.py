# Fixtures for online tests
# Modelled off of interactions.py's test fixtures

import pytest
from interactions import Client, GuildText
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.testing_utils import CapturingContext, generate_dummy_context


@pytest.fixture(scope="module")
async def prefixed_ctx(bot: Client, channel: GuildText) -> PrefixedContext:
    """
    Generic PrefixedContext fixture,
    for commands which do not require any special
    context attributes.

    If you need to test a command which requires
    e.g. a valid message to reply to, create your own.

    Details
    -------
    - Channel ID is set to the channel ID of the channel fixture.
    - User ID is set to the bot's user ID (i.e. the bot is the author of the message).
    - Guild ID is set to the test guild ID.
    - A dummy message ID is generated.
    """
    return generate_dummy_context(
        channel_id=channel.id,
        client=bot,
        user_id=bot.user.id,
        guild_id=TEST_GUILD_ID,
    )


@pytest.fixture(scope="function")
async def capturing_ctx(
    prefixed_ctx: PrefixedContext,
    monkeypatch: pytest.MonkeyPatch,
) -> CapturingContext:
    """
    Patched version of ctx which captures the message
    after sending it to discord.
    it into a `captured_message` attribute.

    Sends the message to Discord as normal.
    (requires HTTP request to Discord)
    """
    with monkeypatch.context() as m:
        m.setattr(
            prefixed_ctx,
            "send",
            CapturingContext.send_and_capture.__get__(prefixed_ctx),
        )
        yield prefixed_ctx


@pytest.fixture(scope="function")
async def offline_ctx(
    prefixed_ctx: PrefixedContext,
    monkeypatch: pytest.MonkeyPatch,
) -> CapturingContext:
    """
    Patched version of ctx which captures the message
    after sending it to discord.
    it into a `captured_message` attribute.

    Also bypasses the HTTP request process to discord,
    useful for testing certain simple cases.
    *Considerably faster than `capturing_ctx` and `ctx`*

    USABLE FOR:
    - message content
    - embeds
    - attachments if you're not downloading them

    NOT USABLE IF YOU NEED TO TEST:
    - attachments with downloaded file contents
    """
    with monkeypatch.context() as m:
        m.setattr(
            prefixed_ctx,
            "send",
            CapturingContext.send_and_capture.__get__(prefixed_ctx),
        )
        m.setattr(
            prefixed_ctx,
            "_send_http_request",
            CapturingContext.fake_send_http_request.__get__(prefixed_ctx),
        )
        yield prefixed_ctx
