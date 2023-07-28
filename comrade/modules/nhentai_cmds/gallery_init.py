import asyncio

from aiohttp import ClientResponseError
from interactions import (
    SlashContext,
)

from comrade.lib.nhentai.page_parser import (
    parse_gallery_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page
from comrade.lib.nhentai.structures import (
    InvalidProxyError,
    NHentaiGallerySession,
    PageParsingError,
)

from .cacher import NHCacher


class NHGalleryInit(NHCacher):
    async def init_gallery_session(
        self,
        ctx: SlashContext,
        gallery_id: int,
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
        send_embed: bool
            Whether or not to send the start embed
        """
        try:
            page = await get_gallery_page(gallery_id, self.bot.http_session)
        except InvalidProxyError:
            return await ctx.send(
                "No NHentai proxies returned a valid response"
            )
        except PageParsingError:
            return await ctx.send(f"Gallery `{gallery_id}` was not found.")
        except ClientResponseError:
            return await ctx.send("HTTP requests to proxies failed.")

        nh_gallery = parse_gallery_from_page(page)

        session = NHentaiGallerySession(nh_gallery)
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
