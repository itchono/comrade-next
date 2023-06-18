import asyncio

import aiohttp
import orjson
import pytest


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
