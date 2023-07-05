import asyncio

from interactions import (
    SlashContext,
)

from comrade.lib.nhentai.page_parser import (
    parse_gallery_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page
from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
)

from .cacher import NHCacher


class NHGalleryInit(NHCacher):
    async def init_gallery_session(
        self,
        ctx: SlashContext,
        gallery_id: int,
        spoiler_imgs: bool = False,
        send_embed: bool = True,
    ):
        """
        Initialize a gallery session in the context, sending the start embed optionally.

        Parameters
        ----------
        ctx: SlashContext
            The SlashContext object
        gallery_id: int
            The gallery ID, aka the 6 digits
        spoiler_imgs: bool
            Whether or not to send images with spoilers
        send_embed: bool
            Whether or not to send the start embed
        """
        page = await get_gallery_page(gallery_id, self.bot.http_session)
        nh_gallery = parse_gallery_from_page(page)

        session = NHentaiGallerySession(
            ctx.author_id, nh_gallery, spoiler_imgs=spoiler_imgs
        )
        self.gallery_sessions[ctx] = session

        if not send_embed:
            return

        await ctx.send(
            embed=nh_gallery.start_embed,
            content="Type `np` (or click the buttons) to"
            " start reading, and advance pages.",
            components=[
                self.prev_page_button(disabled=True),
                self.next_page_button(),
            ],
        )

        # preemptively cache the next few pages (nonblocking)
        asyncio.create_task(self.preemptive_cache(session, lookahead=3))
