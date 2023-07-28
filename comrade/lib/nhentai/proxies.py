from dataclasses import dataclass
from urllib.parse import quote, quote_plus

from aiohttp import ClientSession

from comrade.lib.nhentai.structures import NHentaiSortOrder


@dataclass
class NHentaiSource:
    name: str
    url: str

    async def retrieve_gallery_page(
        self, session: ClientSession, gallery_num: int
    ) -> str:
        """
        Gets the HTML content of an NHentai gallery's main page,
        returning the HTML content as a string.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp ClientSession to use for the request.
        gallery_num : int
            The gallery number of the Nhentai gallery. (e.g. 185217)

        Returns
        -------
        str
            The HTML content of the page.
        """
        async with session.get(f"{self.url}/g/{gallery_num}") as response:
            return await response.text()

    def _get_search_url(
        self, query: str, pagenum: int, sort_order: NHentaiSortOrder
    ) -> str:
        """
        Returns an assembled URL for the search page.

        Parameters
        ----------
        query : str
            The search query to use.
        pagenum : int
            The page number to go to
        sort_order : NHentaiSortOrder
            The sort order to use for the search results.

        Returns
        -------
        str
            The assembled URL.
        """
        # Encode search query so that spaces are replaced with +
        encoded_query = quote_plus(query)

        # Construct the URL to the gallery
        # e.g. nhentai.net/search/?q=alp+love+live
        return (
            f"{self.url}/search/?q={encoded_query}"
            f"&page={pagenum}"
            f"&{sort_order.value}"
        )

    async def retrieve_search_page(
        self,
        session: ClientSession,
        query: str,
        pagenum: int,
        sort_order: NHentaiSortOrder,
    ) -> str:
        """
        Gets the HTML content of an NHentai search page,
        returning the HTML content as a string.

        Parameters
        ----------
        session : aiohttp.ClientSession
            The aiohttp ClientSession to use for the request.
        query : str
            The search query to use.
        pagenum : int
            The page number to go to
        sort_order : NHentaiSortOrder
            The sort order to use for the search results.

        Returns
        -------
        str
            The HTML content of the page.
        """
        search_url = self._get_search_url(query, pagenum, sort_order)
        async with session.get(search_url) as response:
            return await response.text()


@dataclass
class NHentaiMirror(NHentaiSource):
    """
    A mirror of nhentai.net

    Used to distinguish
    generic NHentaiSource from
    a mirror of nhentai.net
    e.g. nhentai.to
    """

    pass


@dataclass
class NHentaiWebProxy(NHentaiSource):
    """
    A proxy of nhentai.net

    Used to distinguish
    generic NHentaiSource from
    a proxy of nhentai.net
    e.g. Yandex Proxy
    """

    pass


@dataclass
class GoogleTranslateProxy(NHentaiWebProxy):
    """
    Special handling for Google Translate
    because of URL encoding issues.
    """

    def _get_search_url(
        self, query: str, pagenum: int, sort_order: NHentaiSortOrder
    ) -> str:
        # We need to encode the search query twice, because
        # the Google Translate proxy will decode it once.
        # Encode the search query so that it can be used in a URL
        # e.g. "alp love live" -> "alp+love+live"
        encoded_search_query = quote_plus(query)

        # url-encode everything to make it compatible with Google Translate
        encoded_search_query = quote(encoded_search_query)
        ampersand = quote("&")

        # Construct the URL to the gallery
        return (
            f"{self.url}/search/?q={encoded_search_query}"
            f"{ampersand}page={pagenum}"
            f"{ampersand}{sort_order.value}"
        )
