import re
from typing import Awaitable, Callable

from interactions import (
    ActionRow,
    ComponentContext,
    Extension,
    Message,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    StringSelectMenu,
    StringSelectOption,
    component_callback,
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
    parse_gallery_from_page,
    parse_maximum_search_pages,
    parse_search_result_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page, get_search_page
from comrade.lib.nhentai.structures import (
    NHentaiGallerySession,
    NHentaiSearchSession,
    NHentaiSortOrder,
)
from comrade.lib.text_utils import text_safe_length

from .page_handler_mixin import PageHandlerMixin


class NHentai(Extension, PageHandlerMixin):
    bot: Comrade

    async def init_gallery_session(
        self,
        ctx: SlashContext,
        gallery_id: int,
        spoiler_imgs: bool = False,
        send_embed: bool = True,
    ):
        """
        Initialize a gallery session in the context, sending the start embed optionally.

        Parameters
        ----------
        ctx: SlashContext
            The SlashContext object
        gallery_id: int
            The gallery ID, aka the 6 digits
        spoiler_imgs: bool
            Whether or not to send images with spoilers
        send_embed: bool
            Whether or not to send the start embed
        """
        page = await get_gallery_page(gallery_id, self.bot.http_session)
        nh_gallery = parse_gallery_from_page(page)

        session = NHentaiGallerySession(
            ctx.author_id, nh_gallery, spoiler_imgs=spoiler_imgs
        )
        self.gallery_sessions[ctx] = session

        if not send_embed:
            return

        await ctx.send(
            embed=nh_gallery.start_embed,
            content="Type `np` (or click the button) to"
            " start reading, and advance pages.",
            components=[self.next_page_button],
        )

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

        await self.send_current_gallery_page(ctx, session)

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

    @component_callback(re.compile(r"nhentai_search_(\d+)"))
    async def nhentai_search_callback(self, ctx: ComponentContext):
        """
        Handles selection callback for the StringSelectMenu in
        an nhentai gallery search.
        """
        # Get the gallery ID from the component value
        gallery_id = int(ctx.values[0])

        # Initialize the session
        await self.init_gallery_session(ctx, gallery_id)

    @component_callback("nhentai_np")
    async def nhentai_np_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            await self.handle_nhentai_next_page(ctx, self.gallery_sessions[ctx])

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new NHentai session.",
                ephemeral=True,
            )
            return

    @listen("message_create")
    async def nhentai_listener(self, message_event: MessageCreate):
        """
        Listens for "np" in channels where a gallery session is active.
        """
        message: Message = message_event.message

        match message.content.lower():
            case "np":
                try:
                    ctx = PrefixedContext.from_message(self.bot, message)
                    # Locate the session
                    nh_gallery_session = self.gallery_sessions[ctx]
                    await self.handle_nhentai_next_page(ctx, nh_gallery_session)

                except KeyError:
                    # No session active
                    pass

    def selector_menu_callback(
        self,
        search_session: NHentaiSearchSession,
        context_id: int,
    ) -> Callable[[int], Awaitable[tuple[list[ActionRow], str]]]:
        """
        Returns a callback used inside the DynamicPaginator
        to get the components and content for the search menu.

        Parameters
        ----------
        search_session: NHentaiSearchSession
            The search session

        context_id: int
            The channel ID of the search session (either guild or DM)

        Returns
        -------
        Callable[[int], Awaitable[tuple[list[ActionRow], str]]]
            The callback function
        """

        async def get_components_and_content(
            page_num: int,
        ) -> tuple[list[ActionRow], str]:
            """
            Gets the components and content for the search menu.

            Assumes that the page has not been requested before.
            """
            # Get the page
            page = await get_search_page(
                search_session.query, page_num, self.bot.http_session
            )
            nh_search_result = parse_search_result_from_page(page)
            search_session.results_pages[page_num] = nh_search_result

            # Create components
            # Each entry in the selector menu will look like:
            # 1. (123456) Title
            #    Title block
            #    <value> = 123456
            numbering_offset = (page_num - 1) * 25  # 25 results per page

            id_name_iter = zip(
                nh_search_result.gallery_ids,
                nh_search_result.short_titles,
                nh_search_result.title_blocks,
            )

            options = [
                StringSelectOption(
                    label=text_safe_length(
                        f"{num+1+numbering_offset}. {short_title}", 100
                    ),
                    value=str(gid),
                    description=text_safe_length(f"({gid}) {title_block}", 100),
                )
                for num, (gid, short_title, title_block) in enumerate(
                    id_name_iter
                )
            ]

            # Give the user a menu to select from
            menu = StringSelectMenu(
                options,
                custom_id=f"nhentai_search_{context_id}",
                placeholder=f"Select a gallery from page {page_num}",
            )

            return (
                [ActionRow(menu)],
                "Select a gallery to view "
                f"(Page {page_num} / {search_session.maximum_pages})",
            )

        return get_components_and_content
