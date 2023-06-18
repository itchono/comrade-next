# Fixtures for online tests
# Taken from https://github.com/interactions-py/interactions.py/blob/stable/tests/test_bot.py

import asyncio
from contextlib import suppress
from pathlib import Path

import pytest
from interactions import Client, Guild, GuildText
from interactions.ext import prefixed_commands

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import BOT_TOKEN, TEST_GUILD_ID
from comrade.lib.discord_utils import generate_dummy_context


@pytest.fixture(scope="session")
async def bot() -> Comrade:
    bot = Comrade()

    prefixed_commands.setup(bot)
    # Load all extensions in the comrade/modules directory
    ext_path = Path(__file__).parent.parent.parent / "comrade" / "modules"

    for module in ext_path.glob("*.py"):
        # Skip __init__.py
        if module.stem == "__init__":
            continue
        bot.load_extension(f"comrade.modules.{module.stem}")

    await bot.login(BOT_TOKEN)
    asyncio.create_task(bot.start_gateway())

    await bot._ready.wait()

    yield bot
    # Teardown
    await bot.stop()


@pytest.fixture(scope="session")
async def guild(bot: Client) -> Guild:
    guild = await bot.fetch_guild(TEST_GUILD_ID)
    return guild


@pytest.fixture(scope="session")
async def channel(guild: Guild) -> GuildText:
    channel = await guild.create_text_channel("auto-testing")
    # TODO: configure channel options like nsfw
    yield channel
    # Teardown
    await channel.delete()


@pytest.fixture(scope="function")
async def ctx(
    bot: Client, channel: GuildText
) -> prefixed_commands.PrefixedContext:
    return generate_dummy_context(channel_id=channel.id, client=bot)
