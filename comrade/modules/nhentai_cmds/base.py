from comrade.core.bot_subclass import Comrade
from comrade.lib.discord_utils import ContextDict
from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
    NHentaiSearchSession,
)


class NHBase:
    bot: Comrade
    gallery_sessions: ContextDict[NHentaiGallerySession] = ContextDict()
    search_sessions: ContextDict[NHentaiSearchSession] = ContextDict()
