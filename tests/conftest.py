import asyncio
from pathlib import Path

import aiohttp
import orjson
import pytest


def pytest_addoption(parser):
    parser.addoption(
        "--include-online", action="store_true", help="Include online tests"
    )


def pytest_ignore_collect(path: Path, config):
    # Ignore online tests if "--include-online" is not passed
    if not config.getoption("--include-online"):
        if path == Path(__file__).parent / "online":
            return True


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
