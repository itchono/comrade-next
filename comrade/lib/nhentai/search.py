from urllib.parse import quote, quote_plus

import aiohttp
import bs4

from comrade.lib.nhentai.page_parser import (
    is_valid_gallery_soup,
    is_valid_search_soup,
)
from comrade.lib.nhentai.structures import (
    NHentaiSortOrder,
    NHentaiWebPage,
    NoGalleryFoundError,
)
from comrade.lib.nhentai.urls import ORDERED_PROXIES


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

    """

    for name, proxy_url_base in ORDERED_PROXIES.items():
        # Construct the URL to the gallery
        # e.g. nhentai.net/g/185217
        req_url = f"{proxy_url_base}/g/{gallery_num}"

        async with http_session.get(req_url) as response:
            html = await response.text()

        soup = bs4.BeautifulSoup(
            html, "lxml"
        )  # lxml is faster than html.parser

        if is_valid_gallery_soup(soup):
            return NHentaiWebPage(name, soup)

    raise NoGalleryFoundError("No valid proxies found")


async def get_search_page(
    search_query: str,
    pagenum: int,
    http_session: aiohttp.ClientSession,
    sort_order: NHentaiSortOrder = NHentaiSortOrder.RECENT,
) -> NHentaiWebPage:
    """
    Gets the HTML content of the NHentai search page, given
    a search query.

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
    """
    # Encode the search query so that it can be used in a URL
    # e.g. "alp love live" -> "alp+love+live"
    encoded_search_query = quote_plus(search_query)

    for name, proxy_url_base in ORDERED_PROXIES.items():
        # SPECIAL CASES, SHOULD FIND A WAY TO GENERALIZE THIS
        # Skip nhentai.to because it has fewer available galleries
        if name == "nhentai.to Mirror":
            continue
        # If it's google translate, encode the plus signs again
        if name == "Google Translate Proxy":
            encoded_search_query = quote(encoded_search_query)
            ampersand = quote("&")
        else:
            ampersand = "&"

        # Construct the URL to the gallery
        # e.g. nhentai.net/search/?q=alp+love+live
        req_url = (
            f"{proxy_url_base}/search/?q={encoded_search_query}"
            f"{ampersand}page={pagenum}"
            f"{ampersand}{sort_order.value}"
        )

        async with http_session.get(req_url) as response:
            html = await response.text()

        soup = bs4.BeautifulSoup(
            html, "lxml"
        )  # lxml is faster than html.parser

        if is_valid_search_soup(soup):
            return NHentaiWebPage(name, soup)

    raise NoGalleryFoundError("No valid proxies found")
