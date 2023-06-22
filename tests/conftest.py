import asyncio

import aiohttp
import orjson
import pytest


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
    loop.close()
