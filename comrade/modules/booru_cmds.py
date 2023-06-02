from urllib.parse import unquote

import booru
from interactions import (
    AutocompleteContext,
    Embed,
    Extension,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    slash_command,
    slash_option,
)

from comrade.lib.online.checks import nsfw_channel
from comrade.lib.standalone.booru_lib import BOORUS


class Booru(Extension):
    @slash_command(description="Gets a random image from a booru")
    @slash_option(
        name="booru_name",
        description="The booru to get the image from",
        required=True,
        opt_type=OptionType.STRING,
        choices=[SlashCommandChoice(name=k, value=k) for k in BOORUS.keys()],
    )
    @slash_option(
        name="tags",
        description="The tags to search for",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    async def booru(self, ctx: SlashContext, booru_name: str, tags: str):
        """
        Get a random image from a chosen booru.

        Parameters
        ----------
        booru : str
            The booru to get the image from.
        tags : str
            The tags to search for.
        """
        if not nsfw_channel(ctx) and booru_name != "safebooru":
            return await ctx.send(
                "This command can only be used in an NSFW channel.",
                ephemeral=True,
            )

        booru_obj = BOORUS[booru_name]()
        img = booru.resolve(await booru_obj.search(query=tags, gacha=True))

        file_url = img["file_url"]
        img_tag_list = ", ".join(img["tags"])

        embed = Embed(title=tags)
        embed.set_image(url=file_url)
        embed.set_footer(text=img_tag_list)

        await ctx.send(embed=embed)

    @booru.autocomplete("tags")
    async def tags_autocomplete(self, ctx: AutocompleteContext):
        """
        Autocomplete handler for the tags option of the booru command.

        Feeds the user suggestions for tags as if they were typing them into
        the booru's search bar.

        This is done by calling the booru's find_tags method, which returns a
        list of tags that match the user's input.
        """
        booru_obj = BOORUS[ctx.kwargs["booru"]]()

        if not hasattr(booru_obj, "find_tags"):
            return await ctx.send(
                ["(This booru does not support tag autocomplete)"]
            )
        elif not ctx.kwargs["tags"]:
            return await ctx.send(["(Start typing to get tag suggestions)"])

        most_recent_tag = (ctx.kwargs["tags"].split()[-1]).strip()
        the_rest = ctx.kwargs["tags"].split()[:-1]
        tags = booru.resolve(await booru_obj.find_tags(most_recent_tag))

        if not tags:
            return await ctx.send([f" ".join(the_rest + [most_recent_tag])])

        to_send = [
            f"{' '.join(the_rest + [unquote(tag)])}" for tag in tags[:10]
        ]

        await ctx.send(to_send)


def setup(bot):
    Booru(bot)
