import re
from dataclasses import dataclass

import bs4

from comrade.lib.nhentai.urls import IMAGE_LINK_BASE

# Regex for extracting gallery ID from href tag
# e.g. <a href="/g/185217/1"> -> 185217
GALLERY_ID_REGEX = re.compile(r"/g/(\d+)/")


# Regex for extracting images ID from URL, based on cover image URL
# e.g. https://t3.nhentai.net/galleries/1019423/cover.jpg -> 1019423
IMAGES_ID_REGEX = re.compile(r"/galleries/(\d+)/cover")

# Regex for extracting image extension and page number from URL
# e.g. https://t3.nhentai.net/galleries/1019423/2t.jpg -> (2), (jpg)
# Must ignore other images
IMAGES_URL_REGEX = re.compile(r"/galleries/\d+/(\d+)(?:t|\.).+")


@dataclass
class NHentaiGallery:
    gallery_id: int  # 6-digit gallery number
    title: str
    images_id: int  # separate from gallery_id, used for image requests
    image_list: str  # list of image URLs corresponding to each page

    @classmethod
    def from_soup(cls, soup: bs4.BeautifulSoup):
        # Determine the title from the first <h1> tag
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

        return cls(gallery_id, title, images_id, image_urls)


@dataclass
class NHentaiGallerySession:

    """
    Per-channel session storage for nhentai commands,
    provided initialization from gallery number.

    Attributes
    ----------
    gallery : NHentaiGallery
        The gallery to use for the session.
    page_number : int
        The page number the session is on.
    """

    gallery: NHentaiGallery
    page_number: int = 1

    @property
    def page_idx(self) -> int:
        return self.page_number - 1

    @classmethod
    async def from_gallery_id(cls, gallery_id: int):
        """
        Initialize the session from a gallery ID.
        """
        gallery = await NHentaiGallery.from_gallery_id(gallery_id)
        return cls(gallery=gallery)


@dataclass
class NHentaiSearchSession:
    """
    Per-channel session storage for nhentai commands,
    provided initialization from search query.

    Attributes
    ----------
    query : str
        The query to use for the session. (e.g. english, translated, etc.)
    num_of_retries : int
        The number of times the session has retried the query.
    """

    query: str
    num_of_retries: int = 0


@dataclass
class NoGalleryFoundError(Exception):
    pass
