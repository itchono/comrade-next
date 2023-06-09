from dataclasses import dataclass
from functools import cached_property
from typing import NamedTuple

from bs4 import BeautifulSoup
from interactions import Embed

from comrade.lib.nhentai.text_filters import filter_title_text


class NHentaiWebPage(NamedTuple):
    provider: str
    soup: BeautifulSoup


@dataclass
class NHentaiGallery:
    gallery_id: int  # 6-digit gallery number
    title: str  # title of the gallery
    images_id: int  # separate from gallery_id, used for image requests
    image_list: list[str]  # list of image URLs corresponding to each page
    tags: list[str]  # list of tags
    provider: str  # provider used to find the gallery

    def __len__(self):
        return len(self.image_list)

    def __getitem__(self, idx):
        return self.image_list[idx]

    def __iter__(self):
        return iter(self.image_list)

    @property
    def url(self) -> str:
        return f"https://nhentai.net/g/{self.gallery_id}/"

    @property
    def cover_url(self) -> str:
        image_extension = self.image_list[0].split(".")[-1]
        return f"https://t.nhentai.net/galleries/{self.images_id}/cover.{image_extension}"

    @cached_property
    def short_title(self) -> str:
        return filter_title_text(self.title)

    @cached_property
    def title_block_tags(self) -> str:
        # Returns parts of the full title minus the short title
        return self.title.replace(self.short_title, "")

    @property
    def start_embed(self) -> Embed:
        embed = Embed(
            title=self.short_title,
            url=self.url,
            description=self.title_block_tags,
        )
        embed.add_field(name="Gallery", value=str(self.gallery_id), inline=True)
        embed.add_field(name="Length", value=f"{len(self)} pages", inline=True)
        embed.add_field(name="Tags", value=", ".join(self.tags), inline=False)

        embed.set_footer(text=f"Found using {self.provider}")

        embed.set_image(url=self.cover_url)

        return embed


@dataclass
class NHentaiGallerySession:

    """
    Per-channel session storage for nhentai commands,
    provided initialization from gallery number.

    Attributes
    ----------
    user_id : int
        The user ID of the session owner.
    gallery : NHentaiGallery
        The gallery to use for the session.
    page_number : int
        The page number the session is on.
    spoiler_imgs : bool
        Whether or not to use spoiler images.
    """

    user_id: int
    gallery: NHentaiGallery
    page_number: int = 0
    spoiler_imgs: bool = False

    @property
    def page_idx(self) -> int:
        return self.page_number - 1

    def advance_page(self) -> bool:
        """
        Advance the page number by one, if possible.

        Returns False if there are no more pages.
        """
        if self.page_number + 1 > len(self.gallery):
            return False

        self.page_number += 1
        return True

    def set_page(self, page_number: int) -> bool:
        """
        Set the page number to a specific page.

        Returns False if the page number is out of bounds.
        """
        if page_number < 0 or page_number > len(self.gallery):
            return False

        self.page_number = page_number
        return True

    @property
    def current_page_url(self) -> str:
        if self.page_number == 0:
            return self.gallery.cover_url
        return self.gallery[self.page_idx]

    @property
    def current_page_filename(self) -> str:
        filename_end = self.current_page_url.split("/")[-1]

        filename = f"{self.gallery.gallery_id}_page_{filename_end}"

        if self.spoiler_imgs:
            return f"SPOILER_{filename}"
        return filename


@dataclass
class NHentaiSearchResult:
    """
    Container for search results.

    Attributes
    ----------
    page_number : int
        The page number the results are on.
        i.e. nth page of search results.
    gallery_ids : list[int]
        List of gallery IDs found on the page.
    titles : list[str]
        List of titles found on the page.
    does_next_page_exist : bool
        Whether or not there is a next page.
    """

    page_number: int
    gallery_ids: list[int]
    titles: list[str]
    does_next_page_exist: bool

    @cached_property
    def short_titles(self) -> list[str]:
        return list(map(filter_title_text, self.titles))

    @cached_property
    def title_blocks(self) -> list[str]:
        return list(
            map(lambda t: t.replace(filter_title_text(t), ""), self.titles)
        )


@dataclass
class NHentaiSearchSession:
    """
    Per-channel session storage for nhentai commands,
    provided initialization from search query.

    Attributes
    ----------
    user_id : int
        The user ID of the session owner.
    query : str
        The query to use for the session. (e.g. english, translated, etc.)
    results_pages : list[NHentaiSearchResult]
        List of search results pages.
    """

    user_id: int
    query: str
    results_pages: list[NHentaiSearchResult]

    @property
    def num_pages_loaded(self) -> int:
        return len(self.results_pages)


class NoGalleryFoundError(Exception):
    pass


class NoSearchResultsError(Exception):
    pass
