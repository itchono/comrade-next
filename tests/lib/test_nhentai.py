import asyncio

from comrade.lib.nhentai.parser import get_valid_nhentai_page, is_valid_page
from comrade.lib.nhentai.structures import NHentaiGallery


def test_gallery_acquisition():
    gallery_id = 185217

    _, page_soup = asyncio.run(get_valid_nhentai_page(gallery_id))

    assert is_valid_page(page_soup)

    gallery = NHentaiGallery.from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title == "(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]"
    )
