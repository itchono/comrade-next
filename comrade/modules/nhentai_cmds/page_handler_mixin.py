from interactions import Button, ButtonStyle, ComponentContext
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.bot_subclass import Comrade
from comrade.lib.discord_utils import ContextDict
from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
    NHentaiSearchSession,
)


class PageHandlerMixin:
    bot: Comrade
    gallery_sessions: ContextDict[NHentaiGallerySession] = ContextDict()
    search_sessions: ContextDict[NHentaiSearchSession] = ContextDict()

    async def send_current_gallery_page(
        self,
        ctx: PrefixedContext | ComponentContext,
        session: NHentaiGallerySession,
    ):
        """
        Sends the currently active page of the gallery session.

        Parameters
        ----------
        ctx: PrefixedContext | ComponentContext
            The context object, originating either from a button or channel message
        session: NHentaiGallerySession
            The gallery session

        """

        # Mirror the image to the bot's blob storage
        blob_url = await self.bot.relay.get_mirrored_blob(
            session.current_page_url,
            filename=session.current_page_filename.split(".")[0],
        )

        await ctx.send(content=blob_url, components=[self.next_page_button])

    async def handle_nhentai_next_page(
        self,
        ctx: PrefixedContext | ComponentContext,
        session: NHentaiGallerySession,
    ):
        """
        Handles the "np" command for nhentai galleries.

        Sends the next image in the gallery,
        and disables the button on the previous message.

        Parameters
        ----------
        ctx: PrefixedContext | ComponentContext
            The context object, originating either from a button or channel message
        session: NHentaiGallerySession
            The gallery session

        """

        # Check if there are more pages
        if not session.advance_page():
            await ctx.send("You have reached the end of this work.")
            del self.gallery_sessions[ctx]
            return

        await self.send_current_gallery_page(ctx, session)

    @property
    def next_page_button(self, disabled: bool = False):
        """
        Button used to advance pages in an nhentai gallery.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Next Page",
            custom_id="nhentai_np",
            disabled=disabled,
        )
