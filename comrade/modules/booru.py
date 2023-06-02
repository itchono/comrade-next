from typing import Type, TypeVar

import booru as booru_lib
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

# Enumate all booru classes
booru_type = TypeVar(
    "booru_type",
    booru_lib.Danbooru,
    booru_lib.Gelbooru,
    booru_lib.Rule34,
    booru_lib.Safebooru,
    booru_lib.Xbooru,
)

# Execute some wizardry using type hints to get a dict of booru names to booru classes
BOORUS: dict[str, Type[booru_type]] = {
    t.__name__.lower(): t for t in booru_type.__constraints__
}


class Booru(Extension):
    @slash_command(description="Gets a random image from a booru")
    @slash_option(
        name="booru",
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
    async def booru(self, ctx: SlashContext, booru: str, tags: str):
        if ctx.guild is not None:
            # Ensure channel is NSFW
            if not ctx.channel.nsfw:
                return await ctx.send(
                    "This command can only be used in NSFW channels",
                    ephemeral=True,
                )

        booru_obj = BOORUS[ctx.kwargs["booru"]]()
        img = booru_lib.resolve(await booru_obj.search(query=tags, gacha=True))

        file_url = img["file_url"]
        img_tag_list = ", ".join(img["tags"])

        embed = Embed(title=tags)
        embed.set_image(url=file_url)
        embed.set_footer(text=img_tag_list)

        await ctx.send(embed=embed)

    @booru.autocomplete("tags")
    async def tags_autocomplete(self, ctx: AutocompleteContext):
        booru_obj = BOORUS[ctx.kwargs["booru"]]()

        if not hasattr(booru_obj, "find_tags"):
            return await ctx.send(
                ["(This booru does not support tag autocomplete)"]
            )
        elif not ctx.kwargs["tags"]:
            return await ctx.send(["(Start typing to get tag suggestions)"])

        most_recent_tag = (ctx.kwargs["tags"].split()[-1]).strip()
        the_rest = ctx.kwargs["tags"].split()[:-1]
        tags = booru_lib.resolve(await booru_obj.find_tags(most_recent_tag))

        if not tags:
            return await ctx.send([f" ".join(the_rest + [most_recent_tag])])

        to_send = [f"{' '.join(the_rest + [tag])}" for tag in tags[:10]]

        await ctx.send(to_send)


def setup(bot):
    Booru(bot)
