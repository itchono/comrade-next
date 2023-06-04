import asyncio

from comrade.lib.nhentai.parser import gallery_from_soup, is_valid_page
from comrade.lib.nhentai.search import get_valid_nhentai_page


def test_gallery_acquisition():
    gallery_id = 185217

    _, page_soup = asyncio.run(get_valid_nhentai_page(gallery_id))

    assert is_valid_page(page_soup)

    gallery = gallery_from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title == "(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]"
    )
