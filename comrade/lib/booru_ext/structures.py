from dataclasses import dataclass
from typing import Type

import booru
from interactions import Embed
from orjson import loads

from comrade.lib.booru_ext.const import OPTIONAL_EMBED_FIELDS
from comrade.lib.booru_ext.filters import clean_up_post_tag
from comrade.lib.discord_utils import SafeLengthEmbed
from comrade.lib.text_utils import escape_md

# Create a type alias that can be any of the booru classes
BooruType = (
    booru.Gelbooru
    | booru.Rule34
    | booru.Safebooru
    | booru.Danbooru
    | booru.Xbooru
)
# Execute some wizardry using type hints to get a dict of booru names to booru classes
BOORUS: dict[str, Type[BooruType]] = {
    t.__name__.lower(): t for t in BooruType.__args__
}


@dataclass
class BooruSession:
    """
    Per-channel session storage for booru commands.

    Attributes
    ----------
    booru : BooruType
        The booru to use for the session.
    query : str
        The query to use for the session.
    sort_random : bool
        Whether to sort the posts randomly.
    page_id : int
        The ID of the page the session is on.
    post_id : int
        The ID of the post the session is on within the page.
    _posts : list[dict[str, str]]
        Storage location for current page of posts.
    """

    booru: BooruType
    query: str
    sort_random: bool = True
    page_id: int = 1
    post_id: int = 0
    _posts: list[dict[str, str]] = None

    async def advance_post(self) -> bool:
        """
        Advance the post ID by one, if possible, and load the new post.
        """
        if self.post_id + 1 >= len(self._posts):
            self.post_id = 0
            return await self.advance_pid()

        self.post_id += 1
        return True

    async def advance_pid(self) -> bool:
        """
        Advance the page ID by one, if possible, and load the new page.

        Returns False if there are no more pages.
        """
        self.page_id += 1
        return await self.init_posts(self.page_id)

    async def init_posts(self, page_id: int, limit_count: int = 100) -> bool:
        """
        Initialize the session, returning False if the query is invalid.
        """
        try:
            posts_raw = await self.booru.search(
                self.query,
                page=page_id,
                limit=limit_count,
                random=self.sort_random,
            )
        except KeyError as e:
            if "0" in str(e):
                return False
            raise e
        except Exception as e:
            if "no results" in str(e):
                return False
            raise e

        # Parse the JSON response
        self._posts = loads(posts_raw)

        return True

    @property
    def post_tags(self) -> str:
        """
        The tags of the current post.

        For Danbooru, make sure to index "tag_string" instead of "tags".
        """
        try:
            return ", ".join(
                map(clean_up_post_tag, self._posts[self.post_id]["tags"])
            )
        except KeyError:
            return ", ".join(
                map(clean_up_post_tag, self._posts[self.post_id]["tag_string"])
            )

    @property
    def formatted_embed(self) -> Embed:
        """
        Create an Embed from a booru post's data.

        Returns
        -------
        Embed
            The embed created from the post data.
        """
        post_data = self._posts[self.post_id]

        footer_text = (
            f"Site: {self.booru.__class__.__name__} | Page {self.page_id} "
            f"| Post {self.post_id + 1} | Type 'next' to advance"
        )

        embed = SafeLengthEmbed(title=escape_md(self.query))
        embed.set_image(url=post_data["file_url"])
        embed.set_footer(text=footer_text)

        embed.add_field(
            name="Tags",
            value=self.post_tags,
            inline=False,
        )

        # Try to add additional fields to the embed, depending on the booru

        for field_name, field_key in OPTIONAL_EMBED_FIELDS.items():
            try:
                embed.add_field(
                    name=field_name, value=post_data[field_key], inline=True
                )
            except KeyError:
                pass

        return embed
