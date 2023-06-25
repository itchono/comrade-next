import pytest
from interactions import Guild
from pymongo import MongoClient
from pymongo.database import Database

from comrade.core.bot_subclass import Comrade
from comrade.core.configuration import MONGODB_URI


@pytest.fixture(scope="session")
async def blank_guild(bot: Comrade) -> Guild:
    """
    Create a blank guild, which is cleaned up after the test
    """
    guild = await Guild.create("Comrade Test Guild Temp", bot)
    yield guild
    await guild.delete()


@pytest.fixture(scope="session")
def mongodb_instance() -> Database:
    mongo_client = MongoClient(MONGODB_URI)  # Connect to MongoDB
    return mongo_client[mongo_client.list_database_names()[0]]
