import asyncio
from contextlib import suppress

import aiohttp
import orjson
import pytest
from interactions import Client, Guild, GuildText

from comrade.bot import main
from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import TEST_GUILD_ID


# Test config options
def pytest_addoption(parser):
    parser.addoption(
        "--run-bot",
        action="store_true",
        help="Run bot integration tests",
    )
    parser.addoption(
        "--run-online",
        action="store_true",
        help="Run tests requiring internet",
    )


# Apply flags
def pytest_collection_modifyitems(config, items):
    # Skip certain tests if the user doesn't specify the option
    if not config.getoption("--run-bot"):
        skip_bot = pytest.mark.skip(reason="need --run-bot option to run")
        for item in items:
            if "bot" in item.keywords:
                item.add_marker(skip_bot)

    if not config.getoption("--run-online"):
        skip_online = pytest.mark.skip(reason="need --run-online option to run")
        for item in items:
            if "online" in item.keywords:
                item.add_marker(skip_online)


# reusable aiohttp client fixture
@pytest.fixture(scope="session")
async def http_session() -> aiohttp.ClientSession:
    client = aiohttp.ClientSession(json_serialize=orjson.dumps)
    yield client
    await client.close()


@pytest.fixture(scope="session")
def event_loop():
    """Overrides pytest default function scoped event loop"""
    policy = asyncio.get_event_loop_policy()
    loop = policy.new_event_loop()
    yield loop

    # Teardown
    with suppress(asyncio.CancelledError):
        # try to finish all pending tasks
        pending_tasks = asyncio.all_tasks(loop=loop)

        # NOTE: reminder tasks loaded by the bot will be pending for a long time
        # so we need to cancel them manually

        if pending_tasks:
            # give the tasks a timeout of 30 seconds
            # to finish before we cancel them
            futures = asyncio.wait(pending_tasks, timeout=30)

            loop.run_until_complete(futures)

    loop.close()


# reusable bot fixture (Comrade instance)
@pytest.fixture(scope="session")
async def bot() -> Comrade:
    # call main() without args
    bot = main(args=[], test_mode=True)
    # Wait for the bot to be ready
    await bot.wait_until_ready()
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
