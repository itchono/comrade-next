from functools import partial

import bs4

from comrade.lib.nhentai.element_parser import (
    get_gallery_id_and_title_from_gallery_div,
    get_gallery_id_from_cover_block,
    get_image_url_from_noscript_block,
    get_images_id_from_noscript_block,
    get_tags_from_a_blocks,
)
from comrade.lib.nhentai.structures import (
    NHentaiGallery,
    NHentaiSearchResult,
    NHentaiWebPage,
)


def is_valid_gallery_soup(soup: bs4.BeautifulSoup) -> bool:
    """
    Returns true if the HTML content of the page represents
    a valid NHentai gallery (i.e. no Cloudflare error page)

    We check for the presence of the <meta> tags describing gallery title, etc.

    There must be at least 3 <meta> tags for the gallery to be valid,
    and should not contain "Just a moment" in the body text.

    There should also not be "404 - Not Found" in the title.

    Parameters
    ----------
    soup : bs4.BeautifulSoup
        The BeautifulSoup object representing the HTML content of the page.

    Returns
    -------
    bool
        True if the page is a valid NHentai gallery, False otherwise.
    """
    meta_tags = soup.find_all("meta")

    if len(meta_tags) < 3:
        return False

    if "Just a moment" in soup.text:
        return False

    # Gallery-specific -- gallery not found
    if "404 - Not Found" in soup.title.text:
        return False

    return True


def is_valid_search_soup(soup: bs4.BeautifulSoup) -> bool:
    """
    Returns true if the HTML content of the page represents
    a valid NHentai search page (i.e. no Cloudflare error page,
    and results are found)


    """
    meta_tags = soup.find_all("meta")

    if len(meta_tags) < 3:
        return False

    negative_results = ["Just a moment", "No results found", "0 Results"]

    for result in negative_results:
        if result in soup.text:
            return False

    return True


def parse_gallery_from_page(page: NHentaiWebPage) -> NHentaiGallery:
    """
    Returns an NHentaiGallery object from the given page.
    """
    soup = page.soup

    title = soup.find("h1").text

    # Find gallery ID, based on the first <a> tag inside the <div> with class "cover"
    # e.g. <a href="/g/185217/1"> -> 185217
    cover_div = soup.find("div", id="cover")
    gallery_id = get_gallery_id_from_cover_block(cover_div)

    # Find the first <noscript> tag to locate a link to the cover,
    # then extract the image ID from the link
    images_id = get_images_id_from_noscript_block(soup.find("noscript"))

    # Construct image URLs from other <noscript> tags
    partial_get_image_url = partial(
        get_image_url_from_noscript_block, images_id=images_id
    )
    # map to function, possibly containins None
    mapped_urls = map(partial_get_image_url, soup.find_all("noscript"))
    image_urls = list(filter(None, mapped_urls))

    # Find tags, based on <a> tags with class "tag"
    tag_a_blocks = soup.find_all("a", class_="tag")
    tags = get_tags_from_a_blocks(tag_a_blocks)

    return NHentaiGallery(
        gallery_id,
        title,
        images_id,
        image_urls,
        tags,
        page.provider,
    )


def parse_search_result_from_page(page: NHentaiWebPage) -> NHentaiSearchResult:
    """
    Extracts search results from a valid NHentai search page.

    Parameters
    ----------
    page : NHentaiWebPage
        The page to extract the search results from.

    Returns
    -------
    NHentaiSearchResult
        The search results.
    """
    soup = page.soup

    # Find the search results container
    search_results_div = soup.find("div", id="content")

    # Find all <div> tags with class "gallery"
    # Each <div> tag represents a single search result
    gallery_divs = search_results_div.find_all("div", class_="gallery")

    # Get the gallery ID and title from each <div> tag
    gallery_ids_titles = list(
        map(get_gallery_id_and_title_from_gallery_div, gallery_divs)
    )
    gallery_ids = [gallery_id for gallery_id, _ in gallery_ids_titles]
    gallery_titles = [title for _, title in gallery_ids_titles]

    # Infer page counts from pagination
    if (
        pagination_section := soup.find("section", class_="pagination")
    ) is None:
        # No pagination, only one page
        return NHentaiSearchResult(1, gallery_ids, gallery_titles, False)

    # Otherwise, there are at least 2 pages
    # Infer current page number from the <a> tag with class "page current"
    current_page_tag = pagination_section.find("a", class_="page current")
    current_page = int(current_page_tag.text)

    # Infer if we are on the last page by trying to find the <a> tag with class "last"
    # If there is no <a> tag with class "last", then we are already on the last page
    on_last_page = pagination_section.find("a", class_="last") is None

    return NHentaiSearchResult(
        current_page, gallery_ids, gallery_titles, not on_last_page
    )
