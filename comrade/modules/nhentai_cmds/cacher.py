from aiohttp import ClientResponseError

from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
)

from .base import NHBase


class NHCacher(NHBase):
    async def preemptive_cache(
        self,
        session: NHentaiGallerySession,
        lookahead: int,
    ) -> list[int]:
        """
        Preemptively caches the next few pages of
        the gallery session.

        Parameters
        ----------
        session: NHentaiGallerySession
            The gallery session
        lookahead: int
            The number of pages to cache ahead of the current page

        Notes
        -----
        Fails silently if the page is already cached,
        or if the page is not found.

        Returns
        -------
        list[int]
            List of page numbers that were cached.

        """
        curr_page_num = session.current_page_number

        nums_cached = []

        for page_num in range(curr_page_num + 1, curr_page_num + lookahead + 1):
            if not session.is_valid_page_number(page_num):
                continue

            page_url = session.page_url(page_num)
            page_filename = session.page_filename(page_num)

            try:
                await self.bot.relay.create_blob_from_url(
                    source_url=page_url, filename=page_filename
                )

                nums_cached.append(page_num)
            except ClientResponseError:
                self.bot.logger.warning(
                    f"[NHENTAI] Could not cache {page_url}"
                    f"for gallery {session.gallery.gallery_id}"
                )
                pass
        return nums_cached
