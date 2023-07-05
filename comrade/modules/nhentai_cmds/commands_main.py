from interactions import (
    Extension,
    Message,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.bot_subclass import Comrade
from comrade.lib.discord_utils import DynamicPaginator, context_id
from comrade.lib.nhentai.page_parser import (
    has_search_results_soup,
    parse_maximum_search_pages,
    parse_search_result_from_page,
)
from comrade.lib.nhentai.search import get_search_page
from comrade.lib.nhentai.structures import (
    NHentaiSearchSession,
    NHentaiSortOrder,
)

from .page_handler import NHPageHandler, PageDirection, PrefetchStrategy
from .search_cmds import NHSearchHandler


class NHentai(Extension, NHSearchHandler, NHPageHandler):
    bot: Comrade

    @slash_command(
        name="nhentai",
        description="NHentai viewer",
        sub_cmd_name="gallery",
        sub_cmd_description="Retrieve an NHentai gallery by gallery number",
        nsfw=True,
    )
    @slash_option(
        name="gallery",
        description="Gallery number, aka the 6 digits",
        required=True,
        opt_type=OptionType.INTEGER,
    )
    @slash_option(
        name="spoiler_imgs",
        description="Send images with spoilers",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    async def nhentai_gallery(
        self, ctx: SlashContext, gallery: int, spoiler_imgs: bool = False
    ):
        """
        Retrieve an nhentai gallery.

        Parameters
        ----------
        gallery: int
            The gallery ID, aka the 6 digits
        spoiler_imgs: bool
            Whether or not to send images with spoilers
        """
        await self.init_gallery_session(ctx, gallery, spoiler_imgs)

    @slash_command(
        name="nhentai",
        description="NHentai viewer",
        sub_cmd_name="gpage",
        sub_cmd_description="Skip to a specific page in the gallery",
        nsfw=True,
    )
    @slash_option(
        name="page",
        description="The page number to skip to",
        required=True,
        opt_type=OptionType.INTEGER,
        min_value=1,
    )
    async def nhentai_gpage(self, ctx: SlashContext, page: int):
        """
        Skip to a specific page in the gallery.

        Parameters
        ----------
        page: int
            The page number to skip to
        """
        session = self.gallery_sessions.get(ctx)

        if not session:
            await ctx.send(
                "You must start a gallery session first using `/nhentai gallery`.",
                ephemeral=True,
            )
            return

        if not session.set_page(page):
            await ctx.send(
                f"Invalid page number. Must be between 1 and {len(session.gallery)}."
            )
            return

        await self.send_current_gallery_page(
            ctx, session, prefetch_strategy=PrefetchStrategy.BOTH
        )

    @slash_command(
        name="nhentai",
        description="NHentai viewer",
        sub_cmd_name="search",
        sub_cmd_description="Search for an NHentai gallery using tags",
        nsfw=True,
    )
    @slash_option(
        name="query",
        description="The search query, just as if you were searching on the site",
        required=True,
        opt_type=OptionType.STRING,
    )
    @slash_option(
        name="sort_order",
        description="The sort order of the search results (default: Popular All Time)",
        required=False,
        opt_type=OptionType.STRING,
        choices=[
            SlashCommandChoice(name=e.pretty_name, value=e.value)
            for e in NHentaiSortOrder
        ],
    )
    async def nhentai_search(
        self,
        ctx: SlashContext,
        query: str,
        sort_order: NHentaiSortOrder = NHentaiSortOrder.POPULAR_ALL_TIME,
    ):
        page = await get_search_page(
            query, 1, self.bot.http_session, sort_order
        )

        if not has_search_results_soup(page.soup):
            return await ctx.send(f"No results found for query `{query}`.")

        nh_search_result = parse_search_result_from_page(page)

        maximum_num_pages = parse_maximum_search_pages(page)

        nh_search_session = NHentaiSearchSession(
            ctx.author_id,
            query,
            {1: nh_search_result},
            maximum_num_pages,
        )

        self.search_sessions[ctx] = nh_search_session

        callback = self.selector_menu_callback(
            nh_search_session, context_id(ctx)
        )

        paginator = DynamicPaginator(
            self.bot, callback, nh_search_session.maximum_pages
        )

        await paginator.send(ctx)

    @listen("message_create")
    async def nhentai_listener(self, message_event: MessageCreate):
        """
        Listens for "np" in channels where a gallery session is active.

        TODO: maybe remove this and just use button navigation?
        """
        message: Message = message_event.message

        match message.content.lower():
            case "np":
                try:
                    ctx = PrefixedContext.from_message(self.bot, message)
                    # Locate the session
                    nh_gallery_session = self.gallery_sessions[ctx]
                    await self.handle_nhentai_change_page(
                        ctx, nh_gallery_session, PageDirection.NEXT
                    )

                except KeyError:
                    # No session active
                    pass
