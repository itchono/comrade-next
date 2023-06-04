from dataclasses import dataclass


@dataclass
class NHentaiGallery:
    gallery_id: int  # 6-digit gallery number
    title: str
    images_id: int  # separate from gallery_id, used for image requests
    image_list: str  # list of image URLs corresponding to each page


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
