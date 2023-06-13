from interactions import Intents

COMRADE_INTENTS = (
    Intents.DEFAULT | Intents.GUILD_MEMBERS | Intents.MESSAGE_CONTENT
)

CLIENT_INIT_KWARGS = {
    "intents": COMRADE_INTENTS,
    "auto_defer": True,
    "sync_ext": True,
    "delete_unused_application_cmds": True,
}
