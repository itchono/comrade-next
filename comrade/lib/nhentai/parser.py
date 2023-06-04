import bs4

from comrade.lib.nhentai.regex import (
    GALLERY_ID_REGEX,
    IMAGES_ID_REGEX,
    IMAGES_URL_REGEX,
)
from comrade.lib.nhentai.structures import NHentaiGallery
from comrade.lib.nhentai.urls import IMAGE_LINK_BASE, ORDERED_PROXIES


def is_valid_page(soup: bs4.BeautifulSoup) -> bool:
    """
    Returns true if the HTML content of the page represents
    a valid NHentai gallery (i.e. no Cloudflare error page)

    We check for the presence of the <meta> tags describing gallery title, etc.

    There must be at least 3 <meta> tags for the gallery to be valid.

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
    return len(meta_tags) >= 3


def gallery_from_soup(soup: bs4.BeautifulSoup) -> NHentaiGallery:
    title = soup.find("h1").text

    # Find gallery ID, based on the first <a> tag inside the <div> with class "cover"
    # e.g. <a href="/g/185217/1"> -> 185217
    cover_div = soup.find("div", id="cover")
    cover_a = cover_div.find("a")
    gallery_id = int(GALLERY_ID_REGEX.search(cover_a["href"]).group(1))

    # Find the first <noscript> tag to locate a link to the cover,
    # then extract the image ID from the link
    images_id_block = soup.find("noscript")
    images_id = int(IMAGES_ID_REGEX.search(str(images_id_block)).group(1))

    # Construct image URLs

    image_urls = []

    # Attempt to find all file extensions
    for block in soup.find_all("noscript"):
        match = IMAGES_URL_REGEX.search(block.text)
        if match:
            page_num = int(match.group(1))
            img_ext = match.group(2)
            image_urls.append(
                f"{IMAGE_LINK_BASE}/{images_id}/{page_num}.{img_ext}"
            )
        continue

    return NHentaiGallery(gallery_id, title, images_id, image_urls)
