from dataclasses import dataclass
from html import unescape
from typing import Type

import booru
from interactions import Embed
from orjson import loads

from comrade.lib.markdown_utils import escape_md

# Create a type alias that can be any of the booru classes
BooruType = (
    booru.Danbooru
    | booru.Gelbooru
    | booru.Rule34
    | booru.Safebooru
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
        except Exception as e:
            if "no results" in e.args[0]:
                return False
            raise e

        # Parse the JSON response
        self._posts = loads(posts_raw)

        return True

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

        file_url = post_data["file_url"]
        img_tag_list = ", ".join(
            map(escape_md, map(unescape, post_data["tags"]))
        )

        footer_text = (
            f"Site: {self.booru.__class__.__name__} | Page {self.page_id} "
            f"| Post {self.post_id + 1} | Type 'next' to advance"
        )

        embed = Embed(title=self.query)
        embed.set_image(url=file_url)
        embed.set_footer(text=footer_text)
        # Truncate the tag list if it's too long
        if len(img_tag_list) > 1000:
            img_tag_list = img_tag_list[:1000] + "..."

        embed.add_field(name="Tags", value=img_tag_list, inline=False)

        # Try to add additional fields to the embed, depending on the booru

        # Post ID
        try:
            embed.add_field(name="Post ID", value=post_data["id"], inline=True)
        except KeyError:
            pass

        # Post Score
        try:
            embed.add_field(name="Score", value=post_data["score"], inline=True)
        except KeyError:
            pass

        return embed
