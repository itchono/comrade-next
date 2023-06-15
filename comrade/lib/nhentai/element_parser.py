import bs4

from comrade.lib.nhentai.regex import (
    GALLERY_ID_REGEX,
    IMAGES_ID_REGEX,
    IMAGES_URL_REGEX,
    TAGS_REGEX,
)
from comrade.lib.nhentai.urls import IMAGE_LINK_BASE


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


def get_gallery_id_and_title_from_gallery_div(
    gallery_div: bs4.Tag,
) -> tuple[int, str]:
    """
    Extracts the gallery id from the gallery div

    Parameters
    ----------
    gallery_div : bs4.Tag
        The gallery div to parse.

    Returns
    -------
    tuple[int, str]
        The gallery id and (full) title.
    """
    # Find the <a> tag with the gallery id
    gallery_a = gallery_div.find("a")

    # Find the <div> tag with the title
    title_div = gallery_div.find("div", class_="caption")
    return (
        int(GALLERY_ID_REGEX.search(gallery_a["href"]).group(1)),
        title_div.text,
    )
