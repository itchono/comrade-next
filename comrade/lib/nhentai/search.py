from logging import getLogger

import aiohttp
import bs4

from comrade.lib.nhentai.page_parser import (
    raise_for_gallery_soup,
    raise_for_search_soup,
)
from comrade.lib.nhentai.proxies import NHentaiWebProxy
from comrade.lib.nhentai.sources import ORDERED_SOURCES
from comrade.lib.nhentai.structures import (
    InvalidProxyError,
    NHentaiSortOrder,
    NHentaiWebPage,
    PageParsingError,
)

logger = getLogger(__name__)


async def get_gallery_page(
    gallery_num: int,
    http_session: aiohttp.ClientSession,
) -> NHentaiWebPage:
    """
    Gets the HTML content of an NHentai gallery's main page.

    Cycles through the proxies in ORDERED_PROXIES until one works.

    Parameters
    ----------
    gallery_num : int
        The gallery number of the Nhentai gallery. (e.g. 185217)
    http_session : aiohttp.ClientSession
        The aiohttp ClientSession to use for the request.

    Returns
    -------
    NHentaiWebPage
        NamedTuple containing the proxy used to access the page, and the BeautifulSoup
        object representing the HTML content of the page.

    Raises
    ------
    InvalidProxyError
        If the proxy itself is invalid.
    PageParsingError
        If the gallery itself is invalid.
    aiohttp.ClientResponseError
        If the proxy returns a non-200 response, e.g. internet is down
    """
    exception_frame: Exception = None

    logger.info(f"Retrieving gallery page for {gallery_num}")

    for proxy in ORDERED_SOURCES:
        try:
            html = await proxy.retrieve_gallery_page(http_session, gallery_num)
        except aiohttp.ClientResponseError as e:
            exception_frame = e
            continue

        soup = bs4.BeautifulSoup(
            html, "lxml"
        )  # lxml is faster than html.parser

        try:
            raise_for_gallery_soup(soup)
        except (InvalidProxyError, PageParsingError) as e:
            exception_frame = e

            logger.warning(f"Proxy {proxy.name} failed: {e}")
            continue
        else:
            logger.debug(f"Proxy {proxy.name} succeeded")
            return NHentaiWebPage(proxy.name, soup)

    raise exception_frame


async def get_search_page(
    search_query: str,
    pagenum: int,
    http_session: aiohttp.ClientSession,
    sort_order: NHentaiSortOrder = NHentaiSortOrder.RECENT,
) -> NHentaiWebPage:
    """
    Gets the HTML content of the NHentai search page, given
    a search query.

    Cycles through the proxies in ORDERED_PROXIES until one works.

    Parameters
    ----------
    search_query : str
        The search query to use for the search page.
        e.g. `alp love live`
    page_num : int
        The page number to use for the search page.
    http_session : aiohttp.ClientSession
        The aiohttp ClientSession to use for the request.
    sort_order : NHentaiSortOrder
        The sort order to use for the search page, default recent

    Returns
    -------
    NHentaiWebPage
        NamedTuple containing the proxy used to access the page, and the BeautifulSoup
        object representing the HTML content of the page.

    Raises
    ------

    """
    exception_frame: Exception = None

    for proxy in ORDERED_SOURCES:
        # Use only instances of NHentaiProxy
        if not isinstance(proxy, NHentaiWebProxy):
            continue

        try:
            html = await proxy.retrieve_search_page(
                http_session, search_query, pagenum, sort_order
            )
        except aiohttp.ClientResponseError as e:
            exception_frame = e
            continue

        soup = bs4.BeautifulSoup(
            html, "lxml"
        )  # lxml is faster than html.parser

        try:
            raise_for_search_soup(soup)
        except (InvalidProxyError, PageParsingError) as e:
            exception_frame = e
            logger.warning(f"Proxy {proxy.name} failed: {e}")
            continue
        else:
            logger.debug(f"Proxy {proxy.name} succeeded")
            return NHentaiWebPage(proxy.name, soup)

    raise exception_frame
