# Fixtures for online tests
# Modelled off of interactions.py's test fixtures

import pytest
from interactions import Client, GuildText
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.testing_utils import CapturingContext, generate_dummy_context


@pytest.fixture(scope="module")
async def ctx(bot: Client, channel: GuildText) -> PrefixedContext:
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
    ctx: PrefixedContext,
    monkeypatch: pytest.MonkeyPatch,
) -> CapturingContext:
    """
    Patched version of ctx which captures the message
    after sending it to discord.
    it into a `testing_captured_message` attribute.

    TODO: try to intercept the message before it's sent to discord
    """
    with monkeypatch.context() as m:
        m.setattr(ctx, "send", CapturingContext.send_and_capture.__get__(ctx))
        yield ctx


@pytest.fixture(scope="function")
async def offline_ctx(
    ctx: PrefixedContext,
    monkeypatch: pytest.MonkeyPatch,
) -> CapturingContext:
    """
    Patched version of ctx which captures the message
    after sending it to discord.
    it into a `testing_captured_message` attribute.

    Also bypasses the HTTP request process to discord,
    useful for testing simple commands which do not
    require followups.
    """
    with monkeypatch.context() as m:
        m.setattr(ctx, "send", CapturingContext.send_and_capture.__get__(ctx))
        m.setattr(
            ctx,
            "_send_http_request",
            CapturingContext.fake_send_http_request.__get__(ctx),
        )
        yield ctx
