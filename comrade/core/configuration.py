from decouple import config

# Production configuration
BOT_TOKEN: str = config("COMRADE_BOT_TOKEN")
MONGODB_URI: str = config("COMRADE_MONGODB_URI")
RELAY_GUILD_ID: int = config("COMRADE_RELAY_GUILD_ID", cast=int)
TIMEZONE: str = config("COMRADE_TIMEZONE", default="UTC")
ACCENT_COLOUR: int = config("COMRADE_ACCENT_COLOUR", cast=int, default=0xD7342A)

# Testing-only
DEV_MODE: bool = config("COMRADE_DEV_MODE", cast=bool, default=False)
TEST_GUILD_ID: int = config("COMRADE_TEST_GUILD_ID", cast=int, default=0)
