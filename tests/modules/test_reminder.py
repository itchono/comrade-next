import pytest
from interactions import BaseContext, InteractionCommand
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.configuration import TEST_GUILD_ID


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
        replyable_ctx, "in 3 seconds", "test reminder"
    )

    # Check that confirmation message was sent
    reminder_confirmation_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert reminder_confirmation_msg.content.startswith(
        "Reminder registered to send"
    )

    def check(m: MessageCreate):
        return m.message._author_id == ctx.bot.user.id and m.message.embeds

    # Wait for bot to send reminder message
    reminder_msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create", checks=check, timeout=5
    )
    # Get latest message in channel
    reminder_embed_msg = reminder_msg_event.message
    embed = reminder_embed_msg.embeds[0]
    assert embed.description == "test reminder"
    assert embed.author.name == f"Reminder for {ctx.author.username}"
