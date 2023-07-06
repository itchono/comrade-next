import asyncio
from collections import deque
from enum import Enum

import arrow
from interactions import (
    ComponentContext,
    component_callback,
)
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
)

from .gallery_init import NHGalleryInit


class PageDirection(Enum):
    NEXT = "next"
    PREV = "prev"


class PrefetchStrategy(Enum):
    NONE = "none"
    LOOKAHEAD = "lookahead"
    LOOKBACK = "lookback"
    BOTH = "both"


class NHPageHandler(NHGalleryInit):
    # store the last 100 page response times
    page_response_times = deque(maxlen=100)

    async def send_current_gallery_page(
        self,
        ctx: PrefixedContext | ComponentContext,
        session: NHentaiGallerySession,
        prefetch_strategy: PrefetchStrategy = PrefetchStrategy.NONE,
    ):
        """
        Sends the currently active page of the gallery session.

        Parameters
        ----------
        ctx: PrefixedContext | ComponentContext
            The context object, originating either from a button or channel message
        session: NHentaiGallerySession
            The gallery session
        prefetch_strategy: PrefetchStrategy
            Whether or not to cache the next few pages,
            and if so, whether to look ahead or look back (or both)

        """
        # Metrics
        start_time = arrow.utcnow()

        # Cache
        blob_url = await self.bot.relay.find_blob_by_url(
            session.current_page_url
        )
        if blob_url is None:
            doc = await self.bot.relay.create_blob_from_url(
                session.current_page_url,
                filename=session.current_page_filename,
            )
            blob_url = doc["blob_url"]

        embed = session.current_page_embed
        embed.set_image(url=blob_url)

        await ctx.send(
            embed=embed,
            components=[
                self.prev_page_button(),
                self.next_page_button(),
            ],
        )

        # Metrics
        end_time = arrow.utcnow()
        self.page_response_times.append((end_time - start_time).total_seconds())

        # Cache images
        if prefetch_strategy == PrefetchStrategy.LOOKAHEAD:
            asyncio.create_task(self.preemptive_cache(session, lookahead=2))
        elif prefetch_strategy == PrefetchStrategy.LOOKBACK:
            asyncio.create_task(self.preemptive_cache(session, lookback=2))
        elif prefetch_strategy == PrefetchStrategy.BOTH:
            asyncio.create_task(
                self.preemptive_cache(session, lookback=2, lookahead=2)
            )

    async def handle_nhentai_change_page(
        self,
        ctx: PrefixedContext | ComponentContext,
        session: NHentaiGallerySession,
        direction: PageDirection,
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
        direction: PageDirection
            The direction to change the page in
            either "next" or "prev"
        """

        if direction == PageDirection.NEXT:
            # Check if there are more pages
            if not session.advance_page():
                await ctx.send("You have reached the end of this work.")
                del self.gallery_sessions[ctx]
                return

            await self.send_current_gallery_page(
                ctx, session, prefetch_strategy=PrefetchStrategy.LOOKAHEAD
            )
        elif direction == PageDirection.PREV:
            if not session.previous_page():
                await ctx.send("You are at the beginning of this work.")
                return

            await self.send_current_gallery_page(
                ctx, session, prefetch_strategy=PrefetchStrategy.LOOKBACK
            )

    @component_callback("nhentai_np")
    async def nhentai_np_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            await self.handle_nhentai_change_page(
                ctx, self.gallery_sessions[ctx], direction=PageDirection.NEXT
            )

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new NHentai session.",
                ephemeral=True,
            )
            return

    @component_callback("nhentai_pp")
    async def nhentai_pp_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            await self.handle_nhentai_change_page(
                ctx, self.gallery_sessions[ctx], direction=PageDirection.PREV
            )

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new NHentai session.",
                ephemeral=True,
            )
            return
