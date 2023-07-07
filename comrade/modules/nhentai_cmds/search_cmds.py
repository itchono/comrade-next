import re
from typing import Awaitable, Callable

from interactions import (
    SELECT_MAX_NAME_LENGTH,
    ActionRow,
    ComponentContext,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    StringSelectMenu,
    StringSelectOption,
    component_callback,
    slash_command,
    slash_option,
)

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
from comrade.lib.text_utils import text_safe_length

from .gallery_init import NHGalleryInit


class NHSearchHandler(NHGalleryInit):
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
        await ctx.defer()  # manually defer, to avoid auto-defer causing issues

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
                        f"{num+1+numbering_offset}. {short_title}",
                        SELECT_MAX_NAME_LENGTH,
                    ),
                    value=str(gid),
                    description=text_safe_length(
                        f"({gid}) {title_block}", SELECT_MAX_NAME_LENGTH
                    ),
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
