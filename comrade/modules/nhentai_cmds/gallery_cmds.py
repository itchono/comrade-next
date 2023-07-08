from interactions import (
    Message,
    OptionType,
    SlashContext,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from .page_handler import NHPageHandler, PageDirection, PrefetchStrategy


class NHGalleryHandler(NHPageHandler):
    @slash_command(
        name="nhentai",
        description="NHentai viewer",
        sub_cmd_name="gallery",
        sub_cmd_description="Retrieve an NHentai gallery by gallery number (ID)",
        nsfw=True,
    )
    @slash_option(
        name="id",
        description="Gallery number, aka the 6 digits",
        required=True,
        opt_type=OptionType.INTEGER,
    )
    async def nhentai_gallery(self, ctx: SlashContext, _id: int):
        """
        Retrieve an nhentai gallery.

        Parameters
        ----------
        _id: int
            The gallery ID, aka the 6 digits
        """
        await self.init_gallery_session(ctx, _id)

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

    @listen("message_create")
    async def nhentai_gallery_listener(self, message_event: MessageCreate):
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
