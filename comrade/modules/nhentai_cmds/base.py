from interactions import (
    Button,
    ButtonStyle,
)

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

    def next_page_button(self, disabled: bool = False):
        """
        Button used to advance pages in an nhentai gallery.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Next",
            custom_id="nhentai_np",
            disabled=disabled,
            emoji="➡️",
        )

    def prev_page_button(self, disabled: bool = False):
        """
        Button used to go back a page in an nhentai gallery.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Previous",
            custom_id="nhentai_pp",
            disabled=disabled,
            emoji="⬅️",
        )
