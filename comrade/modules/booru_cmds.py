from urllib.parse import unquote

from interactions import (
    AutocompleteContext,
    Button,
    ButtonStyle,
    ComponentContext,
    Extension,
    Message,
    OptionType,
    SlashCommandChoice,
    SlashContext,
    component_callback,
    listen,
    slash_command,
    slash_option,
)
from interactions.api.events import MessageCreate
from orjson import loads

from comrade.lib.booru_lib import BOORUS, BooruSession
from comrade.lib.discord_utils import multi_ctx_dispatch


class Booru(Extension):
    booru_sessions: dict[int, BooruSession] = {}

    @slash_command(description="Gets a random image from a booru", nsfw=True)
    @slash_option(
        name="booru_name",
        description="The booru to get the image from",
        required=True,
        opt_type=OptionType.STRING,
        choices=[SlashCommandChoice(name=k, value=k) for k in BOORUS.keys()],
    )
    @slash_option(
        name="tags",
        description="The tags to search for; you can use `*` as a wildcard",
        required=True,
        opt_type=OptionType.STRING,
        autocomplete=True,
    )
    @slash_option(
        name="sort_random",
        description="Whether to sort the posts randomly",
        required=False,
        opt_type=OptionType.BOOLEAN,
    )
    async def booru(
        self,
        ctx: SlashContext,
        booru_name: str,
        tags: str,
        sort_random: bool = True,
    ):
        """
        Get a random image from a chosen booru.

        Parameters
        ----------
        booru : str
            The booru to get the image from.
        tags : str
            The tags to search for.
        """
        booru_obj = BOORUS[booru_name]()
        booru_session = BooruSession(booru_obj, tags, sort_random)

        # Try to initialize the posts list
        if not await booru_session.init_posts(0):
            return await ctx.send("No results found.", ephemeral=True)

        self.booru_sessions[ctx.channel_id] = booru_session

        await ctx.send(
            embed=booru_session.formatted_embed,
            components=[self.next_page_button],
        )

    @booru.autocomplete("tags")
    async def tags_autocomplete(self, ctx: AutocompleteContext):
        """
        Autocomplete handler for the tags option of the booru command.

        Feeds the user suggestions for tags as if they were typing them into
        the booru's search bar.

        This is done by calling the booru's find_tags method, which returns a
        list of tags that match the user's input.
        """
        booru_obj = BOORUS[ctx.kwargs["booru_name"]]()

        query: str = ctx.kwargs["tags"]

        if not hasattr(booru_obj, "find_tags"):
            return await ctx.send(
                ["(This booru does not support tag autocomplete)"]
            )
        elif not query:
            return await ctx.send(["(Start typing to get tag suggestions)"])

        most_recent_tag = (query.split()[-1]).strip()
        the_rest = query.split()[:-1]
        tags = loads(await booru_obj.find_tags(most_recent_tag))

        if not tags:
            return await ctx.send([" ".join(the_rest + [most_recent_tag])])

        to_send = [
            f"{' '.join(the_rest + [unquote(tag)])}" for tag in tags[:10]
        ]

        await ctx.send(to_send)

    async def handle_booru_next(
        self, msg_ctx: Message | ComponentContext, session: BooruSession
    ):
        """
        Handles the "next" command for booru sessions.

        Parameters
        ----------
        message : Message
            The message to handle.
        """
        sendable, channel_id = multi_ctx_dispatch(msg_ctx)

        if not await session.advance_post():
            await sendable.send("No more results found.")
            del self.booru_sessions[channel_id]
            return
        await sendable.send(
            embed=session.formatted_embed, components=[self.next_page_button]
        )

    @property
    def next_page_button(self, disabled: bool = False):
        """
        Button used to advance pages in an nhentai gallery.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Next Post",
            custom_id="booru_next",
            disabled=disabled,
        )

    @listen("message_create")
    async def booru_listener(self, message_event: MessageCreate):
        # Listen for "next" in channels where a booru session is active
        message: Message = message_event.message
        try:
            booru_session = self.booru_sessions[message.channel.id]
            if message.content.lower() == "next":
                await self.handle_booru_next(message, booru_session)
        except KeyError:
            pass

    @component_callback("booru_next")
    async def booru_next_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            booru_session = self.booru_sessions[ctx.channel_id]
            await self.handle_booru_next(ctx, booru_session)

        except KeyError:
            # No session active
            await ctx.send(
                "This button was probably created in the past,"
                " and its session has expired. Please start a new Booru session.",
                ephemeral=True,
            )


def setup(bot):
    Booru(bot)
