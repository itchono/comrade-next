from interactions import (
    ContextMenuContext,
    Embed,
    Extension,
    message_context_menu,
)

from comrade.core.bot_subclass import Comrade
from comrade.lib.tenor import tenor_link_to_gif


class HelpfulConverters(Extension):
    bot: Comrade

    @message_context_menu("Convert to GIF URL")
    async def convert_to_gif_url(self, ctx: ContextMenuContext):
        """
        Convert a Tenor link to a GIF URL
        """
        try:
            url = await tenor_link_to_gif(
                ctx.target.content, self.bot.http_session
            )
            embed = Embed(
                title="Converted to a GIF URL!", description=f"`{url}`"
            )
            embed.set_footer(
                text="You can put this URL whever an image is expected."
            )
            embed.set_image(url=url)
            await ctx.send(embed=embed)

        except ValueError:
            await ctx.send(
                "There is no Tenor link in this message. "
                "Make sure you have selected a message containing a GIF "
                "picked from Discord's GIF picker, and that it is not a GIF "
                "from somewhere else."
            )
