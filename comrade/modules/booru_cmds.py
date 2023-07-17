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
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.comrade_client import Comrade
from comrade.lib.booru_ext import (
    BOORUS,
    BooruSession,
    autocomplete_query,
)
from comrade.lib.discord_utils import ContextDict


class Booru(Extension):
    bot: Comrade
    booru_sessions: ContextDict[BooruSession] = ContextDict()

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
        booru_obj = BOORUS[booru_name](self.bot.http_session)

        # Temporary workaround: sort override
        # If "order:" or "sort:" are in the tags, override the sort_random to be False
        if "order:" in tags or "sort:" in tags:
            sort_random = False

        booru_session = BooruSession(booru_obj, tags, sort_random)

        # Try to initialize the posts list
        if not await booru_session.init_posts(0):
            return await ctx.send("No results found.", ephemeral=True)

        self.booru_sessions[ctx] = booru_session

        await ctx.send(
            embed=booru_session.formatted_embed,
            components=[self.next_post_button],
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
        booru_obj = BOORUS[ctx.kwargs["booru_name"]](self.bot.http_session)

        query: str = ctx.kwargs["tags"]

        if not hasattr(booru_obj, "find_tags"):
            return await ctx.send(
                ["(This booru does not support tag autocomplete)"]
            )
        elif not query:
            return await ctx.send(["(Start typing to get tag suggestions)"])

        query_autocompletes = await autocomplete_query(query, booru_obj)

        await ctx.send(query_autocompletes)

    async def handle_booru_next(
        self, ctx: PrefixedContext | ComponentContext, session: BooruSession
    ):
        """
        Handles the "next" command for booru sessions.

        Parameters
        ----------
        message : Message
            The message to handle.
        """
        if not await session.advance_post():
            await ctx.send("No more results found.")
            del self.booru_sessions[ctx]
            return
        await ctx.send(
            embed=session.formatted_embed,
            components=[self.next_post_button],
        )

    @property
    def next_post_button(self):
        """
        Button used to advance pages in a booru session.
        """
        return Button(
            style=ButtonStyle.PRIMARY,
            label="Next Post",
            custom_id="booru_next",
        )

    @listen("message_create")
    async def booru_listener(self, message_event: MessageCreate):
        # Listen for "next" in channels where a booru session is active
        message: Message = message_event.message

        match message.content.lower():
            case "next":
                ctx = PrefixedContext.from_message(self.bot, message)
                try:
                    booru_session = self.booru_sessions[ctx]
                    await self.handle_booru_next(ctx, booru_session)
                except KeyError:
                    pass

    @component_callback("booru_next")
    async def booru_next_callback(self, ctx: ComponentContext):
        try:
            # Locate the session
            booru_session = self.booru_sessions[ctx]
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
