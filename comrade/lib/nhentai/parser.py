from functools import partial

import bs4

from comrade.lib.nhentai.regex import (
    GALLERY_ID_REGEX,
    IMAGES_ID_REGEX,
    IMAGES_URL_REGEX,
    TAGS_REGEX,
)
from comrade.lib.nhentai.structures import NHentaiGallery
from comrade.lib.nhentai.urls import IMAGE_LINK_BASE


def is_valid_page(soup: bs4.BeautifulSoup) -> bool:
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

    if "404 - Not Found" in soup.title.text:
        return False

    if "Just a moment" in soup.text:
        return False

    return True


def filter_title_text(text: str) -> str:
    """
    Converts the title text from the fully formatted title
    to just the title text.

    The full title text contains text grouped in square brackets and parentheses.
    The title text is the first group of text not enclosed in square brackets or parentheses.

    Ignore all subsequent groups of text that are not enclosed in square brackets or parentheses.

    examples:
    '(C91) [Artist] Title (Group) [English]' -> 'Title'
    '[Artist] Title (Group) [English]' -> 'Title'
    '[Artist] Title [English] not the title' -> 'Title'  # ignore the last group
    """
    title_text = ""

    opening_braces = ["[", "("]
    closing_braces = ["]", ")"]

    brace_stack = []
    corr_opening_brace = {b: c for b, c in zip(closing_braces, opening_braces)}

    for c in text:
        if c in opening_braces:
            brace_stack.append(c)

            # If we already have nontrivial title text, ignore the rest of the text
            if title_text.strip() != "":
                return title_text.strip()
            continue

        elif (brace := corr_opening_brace.get(c)) and brace_stack[-1] == brace:
            brace_stack.pop()
            continue

        if len(brace_stack) == 0:
            title_text += c

    return title_text.strip()


def get_gallery_id_from_cover_block(block: bs4.Tag) -> int:
    """
    Determines the gallery ID from a <div class="cover"> block.

    Parameters
    ----------
    block : bs4.Tag
        The <div class="cover"> block to parse.

    Returns
    -------
    int
        The gallery ID.
    """
    cover_a = block.find("a")
    gallery_id = int(GALLERY_ID_REGEX.search(cover_a["href"]).group(1))

    return gallery_id


def get_images_id_from_noscript_block(block: bs4.Tag) -> int:
    """
    Determines the images ID from a <noscript> block.

    The format is similar to
    <noscript><img src="https://t.nhentai.net/galleries/1019423/cover.jpg" /></noscript>

    Parameters
    ----------
    block : bs4.Tag
        The <noscript> block to parse.

    Returns
    -------
    int
        The images ID.
    """
    images_id = int(IMAGES_ID_REGEX.search(str(block)).group(1))

    return images_id


def get_image_url_from_noscript_block(
    block: bs4.Tag, images_id: int
) -> str | None:
    """
    Constructs an image URL from a <noscript> block.

    Parameters
    ----------
    block : bs4.Tag
        The <noscript> block to parse.
    images_id : int
        The images ID, previously determined from another <noscript> block.

    Returns
    -------
    str
        The image URL, if it could be determined, or None otherwise.
    """
    match = IMAGES_URL_REGEX.search(str(block))

    if not match:
        return None

    page_num = match.group(1)
    img_ext = match.group(2)
    return f"{IMAGE_LINK_BASE}/{images_id}/{page_num}.{img_ext}"


def get_tags_from_a_blocks(tags_a_blocks: list[bs4.Tag]) -> list[str]:
    """
    Gets tags from <a> blocks.

    Parameters
    ----------
    tags_a_blocks : list[bs4.Tag]
        The <a> blocks to parse.

    Returns
    -------
    list[str]
        The tags.
    """
    tags = []
    for tag_a in tags_a_blocks:
        match = TAGS_REGEX.search(tag_a["href"])
        if match:
            tag_str = match.group(1)
            # replace hyphens with spaces
            tag_str = tag_str.replace("-", " ")
            tags.append(tag_str)

    return tags


def get_gallery_from_soup(soup: bs4.BeautifulSoup) -> NHentaiGallery:
    full_title = soup.find("h1").text
    short_title = filter_title_text(full_title)

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
        gallery_id, short_title, full_title, images_id, image_urls, tags
    )
