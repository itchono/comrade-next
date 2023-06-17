from decouple import config

BOT_TOKEN: str = config("COMRADE_BOT_TOKEN")
MONGODB_URI: str = config("COMRADE_MONGODB_URI")
TIMEZONE: str = config("COMRADE_TIMEZONE", default="UTC")
ACCENT_COLOUR: int = config("COMRADE_ACCENT_COLOUR", cast=int, default=0xD7342A)
DEBUG: bool = config("COMRADE_DEBUG", cast=bool, default=False)
TEST_MODE: bool = config("COMRADE_TEST_MODE", cast=bool, default=False)
TEST_GUILD_ID: int = config("COMRADE_TEST_GUILD_ID", cast=int, default=0)
