import aiohttp
import bs4
import orjson

from comrade.lib.nhentai.parser import is_valid_page
from comrade.lib.nhentai.structures import NoGalleryFoundError
from comrade.lib.nhentai.urls import ORDERED_PROXIES


async def get_valid_nhentai_page(
    gallery_num: int,
) -> tuple[str, bs4.BeautifulSoup]:
    """
    Gets the HTML content of an Nhentai gallery's main page.

    Cycles through the proxies in ORDERED_PROXIES until one works.

    Parameters
    ----------
    gallery_num : int
        The gallery number of the Nhentai gallery. (e.g. 185217)

    Returns
    -------
    tuple[str, bs4.BeautifulSoup]
        the proxy used to access the page, and the BeautifulSoup object representing the HTML content of the page.

    """

    for name, proxy_url_base in ORDERED_PROXIES.items():
        # Construct the URL to the gallery
        # e.g. nhenai.net/g/185217
        req_url = f"{proxy_url_base}/g/{gallery_num}"

        async with aiohttp.ClientSession(
            json_serialize=orjson.dumps
        ) as session:
            async with session.get(req_url) as response:
                html = await response.text()

        soup = bs4.BeautifulSoup(
            html, "lxml"
        )  # lxml is faster than html.parser

        if is_valid_page(soup):
            return name, soup

    raise NoGalleryFoundError("No valid proxies found")
