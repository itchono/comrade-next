from interactions import Intents

COMRADE_INTENTS = (
    Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.MESSAGE_CONTENT
)

CLIENT_INIT_KWARGS = {
    "intents": COMRADE_INTENTS,
    "auto_defer": True,
}

MAIN_COLOUR = 0xD7342A  # Red
