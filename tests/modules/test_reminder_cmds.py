import pytest
from interactions import BaseContext, InteractionCommand
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.testing_utils import (
    fetch_latest_message,
    wait_for_message_or_fetch,
)


@pytest.mark.bot
async def test_reminder_from_slash(ctx: BaseContext):
    # We need to create a message to reply to in the context, so this is the workaround.
    msg_to_reply = await ctx.send("Reply to this message with a reminder.")
    replyable_ctx = PrefixedContext.from_message(ctx.bot, msg_to_reply)

    assert replyable_ctx.guild_id == TEST_GUILD_ID

    reminder_slash_cmd: InteractionCommand = ctx.bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["remind"]

    await reminder_slash_cmd.callback(
        replyable_ctx, "in 5 seconds", "test reminder"
    )  # the wait duration might need to change according to ratelimits during testing

    # Check that confirmation message was sent
    reminder_confirmation_msg = await fetch_latest_message(ctx)
    assert reminder_confirmation_msg.content.startswith(
        "Reminder registered to send"
    )

    def check(m: MessageCreate):
        return m.message._author_id == ctx.bot.user.id and m.message.embeds

    reminder_embed_msg = await wait_for_message_or_fetch(ctx, check, timeout=5)
    embed = reminder_embed_msg.embeds[0]
    assert embed.description == "test reminder"
    assert embed.author.name == f"Reminder for {ctx.author.username}"
