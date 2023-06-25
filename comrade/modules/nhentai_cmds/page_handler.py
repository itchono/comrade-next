from interactions import (
    Button,
    ButtonStyle,
    ComponentContext,
    component_callback,
)
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
)

from .gallery_init import NHGalleryInit


class NHPageHandler(NHGalleryInit):
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
        # Cache
        blob_url = await self.bot.relay.find_blob_url(session.current_page_url)
        if blob_url is None:
            doc = await self.bot.relay.create_blob_from_url(
                session.current_page_url,
                filename=session.current_page_filename,
            )
            blob_url = doc["blob_url"]

        embed = session.current_page_embed
        embed.set_image(url=blob_url)

        await ctx.send(embed=embed, components=[self.next_page_button])

        # pre-emptively cache the next two pages
        await self.preemptive_cache(session, lookahead=2)

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

    @component_callback("nhentai_np")
    async def nhentai_np_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            await self.handle_nhentai_next_page(ctx, self.gallery_sessions[ctx])

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new NHentai session.",
                ephemeral=True,
            )
            return
