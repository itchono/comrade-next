from io import BytesIO

import aiohttp
from interactions import (
    Attachment,
    Embed,
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
from orjson import dumps

from comrade.lib.checks import nsfw_channel
from comrade.lib.nhentai.parser import get_gallery_from_soup
from comrade.lib.nhentai.search import get_valid_nhentai_page
from comrade.lib.nhentai.structures import NHentaiGallerySession


class NHentai(Extension):
    nh_gallery_sessions: dict[int, NHentaiGallerySession] = {}

    @slash_command(description="Retrieve an NHentai gallery")
    @slash_option(
        name="gallery",
        description="The gallery ID, aka the 6 digits",
        required=True,
        opt_type=OptionType.INTEGER,
    )
    async def nhentai_gallery(self, ctx: SlashContext, gallery: int):
        """
        Retrieve an nhentai gallery.

        Parameters
        ----------
        gallery: int
            The gallery ID, aka the 6 digits
        """
        if not nsfw_channel(ctx):
            return await ctx.send(
                "This command can only be used in an NSFW channel.",
                ephemeral=True,
            )

        provider, page = await get_valid_nhentai_page(gallery)

        nh_gallery = get_gallery_from_soup(page)

        self.nh_gallery_sessions[ctx.channel_id] = NHentaiGallerySession(
            nh_gallery
        )

        start_embed = Embed(
            title=nh_gallery.title,
            url=nh_gallery.url,
            description=" ".join(nh_gallery.tags),
        )
        start_embed.add_field(name="Length", value=f"{len(nh_gallery)} pages")

        start_embed.set_footer(text=f"Found using {provider}")

        start_embed.set_image(url=nh_gallery.cover_url)

        await ctx.send(embed=start_embed)

    @listen("message_create")
    async def nhentai_listener(self, message_event: MessageCreate):
        # Listen for "next" in channels where a booru session is active
        message: Message = message_event.message
        try:
            nh_gallery_session = self.nh_gallery_sessions[message.channel.id]
            if message.content.lower() == "np":
                if not nh_gallery_session.advance_page():
                    await message.channel.send("No more results found.")
                    del self.nh_gallery_sessions[message.channel.id]
                    return

                # Request the image
                async with aiohttp.ClientSession(
                    json_serialize=dumps
                ) as session:
                    async with session.get(
                        nh_gallery_session.current_page
                    ) as resp:
                        img_io = BytesIO(await resp.read())
                img_io.seek(0)

                img_file = File(img_io, file_name="image.png")

                await message.channel.send(file=img_file)
        except KeyError:
            pass


def setup(bot):
    NHentai(bot)
