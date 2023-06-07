from dataclasses import dataclass

from interactions import Embed


@dataclass
class NHentaiGallery:
    gallery_id: int  # 6-digit gallery number
    short_title: str  # title of the gallery, without tag blocks
    full_title: str  # title of the gallery
    images_id: int  # separate from gallery_id, used for image requests
    image_list: list[str]  # list of image URLs corresponding to each page
    tags: list[str]  # list of tags
    provider: str = "nhentai.net"  # provider used to find the gallery

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

    @property
    def title_block_tags(self) -> str:
        # Returns parts of the full title minus the short title
        return self.full_title.replace(self.short_title, "")

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
    gallery : NHentaiGallery
        The gallery to use for the session.
    page_number : int
        The page number the session is on.
    spoiler_imgs : bool
        Whether or not to use spoiler images.
    """

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

    @property
    def current_page(self) -> str:
        if self.page_number == 0:
            return self.gallery.cover_url
        return self.gallery[self.page_idx]

    @property
    def current_filename(self) -> str:
        filename_end = self.current_page.split("/")[-1]

        filename = f"{self.gallery.gallery_id}_page_{filename_end}"

        if self.spoiler_imgs:
            return f"SPOILER_{filename}"
        return filename


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
