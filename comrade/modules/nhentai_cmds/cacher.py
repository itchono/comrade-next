from logging import getLogger

from aiohttp import ClientResponseError

from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
)

from .base import NHBase

logger = getLogger(__name__)


class NHCacher(NHBase):
    async def preemptive_cache(
        self,
        session: NHentaiGallerySession,
        lookback: int = 0,
        lookahead: int = 0,
    ) -> tuple[list[int], list[int]]:
        """
        Preemptively caches the next few/previous pages of
        the gallery session.

        Parameters
        ----------
        session: NHentaiGallerySession
            The gallery session
        lookback: int
            The number of pages to cache before the current page
        lookahead: int
            The number of pages to cache after the current page

        Notes
        -----
        Fails silently if the pages are already cached,
        or if the page is not found.

        Returns
        -------
        list[int]
            List of page numbers that were newly cached.
        list[int]
            List of page numbers that were already cached.

        """
        curr_page_num = session.current_page_number

        nums_cached = []
        nums_loaded = []

        pages_to_cache = range(
            curr_page_num - lookback, curr_page_num + 1 + lookahead
        )

        for page_num in pages_to_cache:
            if (
                not session.is_valid_page_number(page_num)
                or page_num == curr_page_num
            ):
                continue

            page_url = session.page_url(page_num)
            page_filename = session.page_filename(page_num)

            # check if the page is already cached
            if await self.bot.relay.find_blob_by_url(page_url):
                nums_loaded.append(page_num)
                continue

            # otherwise, cache it
            try:
                await self.bot.relay.create_blob_from_url(
                    source_url=page_url, filename=page_filename
                )

                nums_cached.append(page_num)
            except ClientResponseError:
                logger.warning(
                    f"Could not cache {page_url}"
                    f"for gallery {session.gallery.gallery_id}"
                )
                pass

        return nums_cached, nums_loaded
