import re
from io import BytesIO

from interactions import (
    Button,
    ButtonStyle,
    ComponentContext,
    Extension,
    File,
    Message,
    OptionType,
    SlashContext,
    StringSelectMenu,
    StringSelectOption,
    component_callback,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate

from comrade.core.bot_subclass import Comrade
from comrade.lib.checks import nsfw_channel
from comrade.lib.nhentai.page_parser import (
    parse_gallery_from_page,
    parse_search_result_from_page,
)
from comrade.lib.nhentai.search import get_gallery_page, get_search_page
from comrade.lib.nhentai.structures import NHentaiGallerySession
from comrade.lib.text_utils import text_safe_length


class NHentai(Extension):
    bot: Comrade
    gallery_sessions: dict[int, NHentaiGallerySession] = {}

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
        self.gallery_sessions[ctx.channel_id] = session

        if not send_embed:
            return

        await ctx.send(
            embed=nh_gallery.start_embed,
            content="Type `np` (or click the button) to"
            " start reading, and advance pages.",
            components=[self.next_page_button()],
        )

    @slash_command(description="Retrieve an NHentai gallery")
    @slash_option(
        name="gallery",
        description="The gallery ID, aka the 6 digits",
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
        if not nsfw_channel(ctx):
            return await ctx.send(
                "This command can only be used in an NSFW channel.",
                ephemeral=True,
            )
        await self.init_gallery_session(ctx, gallery, spoiler_imgs)

    @slash_command(description="Search for an NHentai gallery")
    @slash_option(
        name="query",
        description="The search query",
        required=True,
        opt_type=OptionType.STRING,
    )
    async def nhentai_search(self, ctx: SlashContext, query: str):
        if not nsfw_channel(ctx):
            return await ctx.send(
                "This command can only be used in an NSFW channel.",
                ephemeral=True,
            )

        page = await get_search_page(query, 1, self.bot.http_session)
        nh_search_result = parse_search_result_from_page(page)

        if not nh_search_result.gallery_ids:
            return await ctx.send("No results found.")

        id_name_iter = zip(
            nh_search_result.gallery_ids,
            nh_search_result.short_titles,
            nh_search_result.title_blocks,
        )
        options = [
            StringSelectOption(
                label=text_safe_length(f"{num+1}. ({gid}) {short_title}", 100),
                value=str(gid),
                description=text_safe_length(title_block, 100),
            )
            for num, (gid, short_title, title_block) in enumerate(id_name_iter)
        ]

        # Give the user a menu to select from
        menu = StringSelectMenu(
            options,
            custom_id=f"nhentai_search_{ctx.channel_id}",
            placeholder="Select a gallery",
        )

        # Give the option to advance pages
        await ctx.send(content="Select a gallery to view", components=[menu])

    async def handle_nhentai_next_page(
        self,
        msg_ctx: Message | ComponentContext,
        session: NHentaiGallerySession,
    ):
        """
        Handles the "np" command for nhentai galleries.

        Sends the next image in the gallery,
        and disables the button on the previous message.

        Parameters
        ----------
        msg_ctx: Message | ComponentContext
            The message or component context calling the command
        session: NHentaiGallerySession
            The gallery session

        """
        # Multiple dispatch handler
        if isinstance(msg_ctx, Message):
            sendable = msg_ctx.channel
            channel_id = sendable.id
        else:
            sendable = msg_ctx
            channel_id = msg_ctx.channel_id

        # Check if there are more pages
        if not session.advance_page():
            await sendable.send("No more results found.")
            del self.gallery_sessions[channel_id]
            return

        # Request and send the image
        async with self.bot.http_session.get(session.current_page_url) as resp:
            img_bytes = BytesIO(await resp.read())
        img_file = File(img_bytes, file_name=session.current_page_filename)

        await sendable.send(file=img_file, components=[self.next_page_button()])

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

    def next_page_button(self, disabled: bool = False):
        """
        Button used to advance pages in an nhentai gallery.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Next Page",
            custom_id="nhentai_np",
            disabled=disabled,
        )

    @component_callback("nhentai_np")
    async def nhentai_np_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            nh_gallery_session = self.gallery_sessions[ctx.channel_id]
            await self.handle_nhentai_next_page(ctx, nh_gallery_session)

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new NHentai session.",
                ephemeral=True,
            )

    @listen("message_create")
    async def nhentai_listener(self, message_event: MessageCreate):
        """
        Listens for "np" in channels where a gallery session is active.
        """
        message: Message = message_event.message
        try:
            # Locate the session
            nh_gallery_session = self.gallery_sessions[message.channel.id]

            if message.content.lower() == "np":
                await self.handle_nhentai_next_page(message, nh_gallery_session)

        except KeyError:
            # No session active
            pass


def setup(bot):
    NHentai(bot)
