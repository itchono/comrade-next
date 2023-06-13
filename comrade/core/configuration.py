from decouple import config

BOT_TOKEN = config("COMRADE_BOT_TOKEN")
MONGODB_URI = config("COMRADE_MONGODB_URI")
TIMEZONE = config("COMRADE_TIMEZONE", default="UTC")
ACCENT_COLOUR = config("COMRADE_ACCENT_COLOUR", cast=int, default=0xD7342A)
DEBUG = config("COMRADE_DEBUG", cast=bool, default=False)
DEBUG_SCOPE = config("COMRADE_DEBUG_SCOPE", cast=int, default=0)
