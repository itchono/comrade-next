# Fixtures for online tests
# Modelled off of interactions.py's test fixtures

import pytest
from interactions import Client, GuildText
from interactions.ext import prefixed_commands

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.discord_utils import generate_dummy_context


@pytest.fixture(scope="function")
async def ctx(
    bot: Client, channel: GuildText
) -> prefixed_commands.PrefixedContext:
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
