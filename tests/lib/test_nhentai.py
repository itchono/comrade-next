import asyncio

import pytest

from comrade.lib.nhentai.parser import get_gallery_from_soup, is_valid_page
from comrade.lib.nhentai.search import get_valid_nhentai_page
from comrade.lib.nhentai.structures import NoGalleryFoundError


def test_gallery_acquisition_nominal():
    """
    Tests accessing a gallery that is on nhentai.to (primary mirror)

    Verifies that page count and first image url is correct
    """
    gallery_id = 185217

    proxy_name, page_soup = asyncio.run(get_valid_nhentai_page(gallery_id))

    assert proxy_name == "nhentai.to"
    assert is_valid_page(page_soup)

    gallery = get_gallery_from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title == "(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]"
    )

    assert (
        gallery.image_list[0] == "https://i.nhentai.net/galleries/1019423/1.jpg"
    )

    assert len(gallery) == 28


def test_not_present_anywhere():
    """
    Verify that a gallery that is not present on any mirror raises an exception
    """
    gallery_id = -1

    with pytest.raises(NoGalleryFoundError):
        asyncio.run(get_valid_nhentai_page(gallery_id))


def test_gallery_not_on_nhentai_to():
    gallery_id = 444797

    proxy_name, page_soup = asyncio.run(get_valid_nhentai_page(gallery_id))

    assert proxy_name == "Google Translate Proxy"

    assert is_valid_page(page_soup)

    gallery = get_gallery_from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title
        == "[Michiking] Ane Taiken Jogakuryou | Older Sister Experience - The Girls' Dormitory [English] [Yuzuru Katsuragi] [Digital]"
    )

    assert (
        gallery.image_list[0] == "https://i.nhentai.net/galleries/2485699/1.jpg"
    )

    assert len(gallery) == 313
