import aiohttp
import pytest

from comrade.lib.nhentai.page_parser import (
    has_search_results_soup,
    is_valid_gallery_soup,
    parse_gallery_from_page,
    parse_maximum_search_pages,
    parse_search_result_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page, get_search_page
from comrade.lib.nhentai.structures import (
    NoGalleryFoundError,
    NoSearchResultsError,
)
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
    num_pages = parse_maximum_search_pages(page)

    assert 388445 in search_result.gallery_ids
    assert num_pages == 1


async def test_search_nominal_2(http_session: aiohttp.ClientSession):
    search_query = "school swimsuit"

    page = await get_search_page(search_query, 1, http_session)
    num_pages = parse_maximum_search_pages(page)
    assert num_pages > 1

    parse_search_result_from_page(page)


async def test_search_negative(http_session: aiohttp.ClientSession):
    search_query = "this should not exist"

    page = await get_search_page(search_query, 1, http_session)
    assert not has_search_results_soup(page.soup)

    with pytest.raises(NoSearchResultsError):
        parse_maximum_search_pages(page)
    with pytest.raises(NoSearchResultsError):
        parse_search_result_from_page(page)
