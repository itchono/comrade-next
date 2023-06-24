import asyncio

import pytest
from interactions import Client
from pymongo import MongoClient
from pymongo.database import Database

from comrade.core.configuration import BOT_TOKEN, MONGODB_URI


@pytest.fixture(scope="session")
async def generic_bot() -> Client:
    # call main() without args
    bot = Client()

    asyncio.create_task(bot.login(token=BOT_TOKEN))
    asyncio.create_task(bot.start_gateway())
    # Wait for the bot to be ready
    await bot.wait_until_ready()
    yield bot

    # Teardown
    await bot.stop()


@pytest.fixture(scope="session")
def mongodb_instance() -> Database:
    mongo_client = MongoClient(MONGODB_URI)  # Connect to MongoDB
    return mongo_client[mongo_client.list_database_names()[0]]
