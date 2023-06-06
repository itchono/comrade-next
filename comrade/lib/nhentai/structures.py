from dataclasses import dataclass

from comrade.lib.nhentai.urls import IMAGE_LINK_BASE


@dataclass
class NHentaiGallery:
    gallery_id: int  # 6-digit gallery number
    title: str  # title of the gallery
    images_id: int  # separate from gallery_id, used for image requests
    image_list: list[str]  # list of image URLs corresponding to each page
    tags: list[str]  # list of tags

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
        return IMAGE_LINK_BASE + f"/{self.images_id}/cover.jpg"


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

    def advance_page(self) -> bool:
        """
        Advance the page number by one, if possible.

        Returns False if there are no more pages.
        """
        if self.page_number + 1 > len(self.gallery):
            return False

        self.page_number += 1
        return True

    @property
    def current_page(self) -> str:
        return self.gallery[self.page_idx]


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


class NoGalleryFoundError(Exception):
    pass
