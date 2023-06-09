import aiohttp
import pytest

from comrade.lib.nhentai.page_parser import (
    is_valid_gallery_soup,
    parse_gallery_from_page,
    parse_search_result_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page, get_search_page
from comrade.lib.nhentai.structures import NoGalleryFoundError
from comrade.lib.nhentai.text_filters import filter_title_text


@pytest.mark.parametrize(
    "full_title, expected_title",
    [
        ("(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]", "R.E.I.N.A"),
        (
            "[Morittokoke (Morikoke)] Hyrule Hanei no Tame no Katsudou! | "
            "Taking Steps to Ensure Hyrule's Prosperity! "
            "(The Legend of Zelda) [English] =The Lost Light= [Digital]",
            "Hyrule Hanei no Tame no Katsudou! | "
            "Taking Steps to Ensure Hyrule's Prosperity!",
        ),
    ],
)
def test_title_parser(full_title, expected_title):
    assert filter_title_text(full_title) == expected_title


async def test_gallery_acquisition_nominal(
    http_session: aiohttp.ClientSession,
):
    """
    Tests accessing a gallery that is on nhentai.to (primary mirror)

    Verifies that page count and first image url is correct
    """
    gallery_id = 185217

    page = await get_gallery_page(gallery_id, http_session)

    assert page.provider == "nhentai.to Mirror"
    assert is_valid_gallery_soup(page.soup)

    gallery = parse_gallery_from_page(page)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title == "(C91) [HitenKei (Hiten)] R.E.I.N.A [English] [Scrubs]"
    )

    assert (
        gallery.image_list[0]
        == "https://i3.nhentai.net/galleries/1019423/1.jpg"
    )

    assert len(gallery) == 28


async def test_not_present_anywhere(http_session: aiohttp.ClientSession):
    """
    Verify that a gallery that is not present on any mirror raises an exception
    """
    gallery_id = -1

    with pytest.raises(NoGalleryFoundError):
        await get_gallery_page(gallery_id, http_session)


async def test_gallery_not_on_nhentai_to(http_session: aiohttp.ClientSession):
    gallery_id = 444797

    page = await get_gallery_page(gallery_id, http_session)

    assert page.provider == "Google Translate Proxy"

    assert is_valid_gallery_soup(page.soup)

    gallery = parse_gallery_from_page(page)

    assert gallery.gallery_id == gallery_id
    assert (
        gallery.title
        == "[Michiking] Ane Taiken Jogakuryou | Older Sister Experience"
        " - The Girls' Dormitory [English] [Yuzuru Katsuragi] [Digital]"
    )

    assert (
        gallery.image_list[0]
        == "https://i3.nhentai.net/galleries/2485699/1.jpg"
    )

    assert len(gallery) == 313


async def test_search_nominal_1(http_session: aiohttp.ClientSession):
    search_query = "alp love live english kurosawa"

    page = await get_search_page(search_query, 1, http_session)

    search_result = parse_search_result_from_page(page)

    assert 388445 in search_result.gallery_ids
    assert not search_result.does_next_page_exist


async def test_search_nominal_2(http_session: aiohttp.ClientSession):
    search_query = "school swimsuit"

    page = await get_search_page(search_query, 1, http_session)

    search_result = parse_search_result_from_page(page)
    assert search_result.does_next_page_exist
