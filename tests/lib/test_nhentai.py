import asyncio

import aiohttp
import pytest

from comrade.lib.nhentai.parser import (
    filter_title_text,
    get_gallery_from_soup,
    is_valid_page,
)
from comrade.lib.nhentai.search import get_valid_nhentai_page
from comrade.lib.nhentai.structures import NoGalleryFoundError


async def get_page_coro(gallery_id):
    """
    Helper function for testing without async tests
    """
    async with aiohttp.ClientSession() as http_session:
        return await get_valid_nhentai_page(gallery_id, http_session)


@pytest.mark.parametrize(
    "full_title, expected_title",
    [
        ("(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]", "R.E.I.N.A"),
        (
            "[Morittokoke (Morikoke)] Hyrule Hanei no Tame no Katsudou! | "
            "Taking Steps to Ensure Hyrule's Prosperity! (The Legend of Zelda) [English] =The Lost Light= [Digital]",
            "Hyrule Hanei no Tame no Katsudou! | Taking Steps to Ensure Hyrule's Prosperity!",
        ),
    ],
)
def test_title_parser(full_title, expected_title):
    assert filter_title_text(full_title) == expected_title


def test_gallery_acquisition_nominal():
    """
    Tests accessing a gallery that is on nhentai.to (primary mirror)

    Verifies that page count and first image url is correct
    """
    gallery_id = 185217

    proxy_name, page_soup = asyncio.run(get_page_coro(gallery_id))

    assert proxy_name == "nhentai.to"
    assert is_valid_page(page_soup)

    gallery = get_gallery_from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.full_title
        == "(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]"
    )

    assert (
        gallery.image_list[0]
        == "https://i3.nhentai.net/galleries/1019423/1.jpg"
    )

    assert len(gallery) == 28


def test_not_present_anywhere():
    """
    Verify that a gallery that is not present on any mirror raises an exception
    """
    gallery_id = -1

    with pytest.raises(NoGalleryFoundError):
        asyncio.run(get_page_coro(gallery_id))


def test_gallery_not_on_nhentai_to():
    gallery_id = 444797

    proxy_name, page_soup = asyncio.run(get_page_coro(gallery_id))

    assert proxy_name == "Google Translate Proxy"

    assert is_valid_page(page_soup)

    gallery = get_gallery_from_soup(page_soup)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.full_title
        == "[Michiking] Ane Taiken Jogakuryou | Older Sister Experience - The Girls' Dormitory [English] [Yuzuru Katsuragi] [Digital]"
    )

    assert (
        gallery.image_list[0]
        == "https://i3.nhentai.net/galleries/2485699/1.jpg"
    )

    assert len(gallery) == 313
