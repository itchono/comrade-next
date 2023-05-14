from nextcord.ext.commands import Bot
from pymongo import MongoClient
from urllib.parse import quote_plus
from os import getenv


class Comrade(Bot):
    """
    Modified subclass of Nextcord bot to have a few extra features.

    Extra Additions
    ---------------
    - MongoDB connection
    - Configuration store
    - logging
    """

    db: MongoClient

    def __init__(self, *args, **kwargs):
        # Init Nextcord Bot class
        super().__init__(*args, **kwargs)

        # Comrade-specific init

        # Connect to MongoDB
        # must parse the password to avoid issues with special characters
        try:
            mongokey = kwargs["mongodb_key"]
        except KeyError:
            mongokey = getenv("MONGODB_KEY")

        self.db = MongoClient(quote_plus(mongokey))
