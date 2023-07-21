import pytest
from interactions import InteractionCommand
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.configuration import TEST_GUILD_ID
from comrade.lib.testing_utils import (
    CapturingContext,
    wait_for_message_or_fetch,
)


@pytest.mark.bot
async def test_reminder_from_slash(
    prefixed_ctx: PrefixedContext, monkeypatch: pytest.MonkeyPatch
):
    # We need to create a message to reply to in the context, so this is the workaround.
    msg_to_reply = await prefixed_ctx.send(
        "Reply to this message with a reminder."
    )
    replyable_ctx: CapturingContext = PrefixedContext.from_message(
        prefixed_ctx.bot, msg_to_reply
    )

    assert replyable_ctx.guild_id == TEST_GUILD_ID

    reminder_slash_cmd: InteractionCommand = (
        prefixed_ctx.bot.interactions_by_scope[TEST_GUILD_ID]["remind"]
    )

    # monkeypatch replyable_ctx.send to capture the message
    with monkeypatch.context() as m:
        m.setattr(
            replyable_ctx,
            "send",
            CapturingContext.send_and_capture.__get__(replyable_ctx),
        )

        await reminder_slash_cmd.callback(
            replyable_ctx, "in 5 seconds", "test reminder"
        )  # the wait duration might need to change according to ratelimits during testing

        # Check that confirmation message was sent
        reminder_confirmation_msg = replyable_ctx.captured_message
        assert reminder_confirmation_msg.content.startswith(
            "Reminder registered to send"
        )

    def check(m: MessageCreate):
        return (
            m.message.author == prefixed_ctx.bot.user
            and m.message.embeds
            and m.message.channel == prefixed_ctx.channel
        )

    reminder_embed_msg = await wait_for_message_or_fetch(
        prefixed_ctx, check, timeout=5
    )
    embed = reminder_embed_msg.embeds[0]
    assert embed.description == "test reminder"
    assert embed.author.name == f"Reminder for {prefixed_ctx.author.username}"
