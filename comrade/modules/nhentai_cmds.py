from io import BytesIO

from interactions import (
    Extension,
    File,
    Message,
    OptionType,
    SlashContext,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate

from comrade.core.bot_subclass import Comrade
from comrade.lib.checks import nsfw_channel
from comrade.lib.nhentai.parser import get_gallery_from_soup
from comrade.lib.nhentai.search import get_valid_nhentai_page
from comrade.lib.nhentai.structures import NHentaiGallerySession


class NHentai(Extension):
    bot: Comrade
    gallery_sessions: dict[int, NHentaiGallerySession] = {}

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

        provider, page = await get_valid_nhentai_page(
            gallery, self.bot.aiohttp_session
        )

        nh_gallery = get_gallery_from_soup(page)
        nh_gallery.provider = provider

        session = NHentaiGallerySession(nh_gallery, spoiler_imgs=spoiler_imgs)
        self.gallery_sessions[ctx.channel_id] = session

        await ctx.send(
            embed=nh_gallery.start_embed,
            content="Type `np` to start reading, and advance pages.",
        )

    async def handle_nhentai_np(
        self, message: Message, session: NHentaiGallerySession
    ):
        """
        Handles the "np" command for nhentai galleries.

        Parameters
        ----------
        message: Message
            The message object
        session: NHentaiGallerySession
            The gallery session

        """
        if not session.advance_page():
            await message.channel.send("No more results found.")
            del self.gallery_sessions[message.channel.id]
            return

        # Request the image
        img_url = session.current_page

        async with self.bot.aiohttp_session.get(img_url) as resp:
            img_io = BytesIO(await resp.read())
        img_io.seek(0)

        # Send the image
        img_file = File(img_io, file_name=session.current_filename)

        await message.channel.send(file=img_file)

    @listen("message_create")
    async def nhentai_listener(self, message_event: MessageCreate):
        # Listen for "next" in channels where a booru session is active
        message: Message = message_event.message
        try:
            # Locate the session
            nh_gallery_session = self.gallery_sessions[message.channel.id]

            if message.content.lower() == "np":
                await self.handle_nhentai_np(message, nh_gallery_session)

        except KeyError:
            # No session active
            pass


def setup(bot):
    NHentai(bot)
