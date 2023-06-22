import asyncio

import pytest
from interactions import BaseContext
from interactions.api.events import MessageCreate


@pytest.mark.bot
@pytest.mark.parametrize("emote", ("pssh", "PSSH"))
async def test_sending_emote(ctx: BaseContext, emote: str):
    """
    Tests sending an emote from the bot,
    with both case-sensitive and case-insensitive emote names.
    """
    await ctx.send(f":{emote}:")

    def check(m: MessageCreate):
        return m.message.webhook_id is not None

    # Wait for bot to send message
    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create", checks=check, timeout=5
    )

    emoji_msg = msg_event.message
    assert (
        emoji_msg.content
        == "https://cdn.discordapp.com/attachments/810726667026300958/810732433460559872/pssh.png"
    )

    await asyncio.sleep(1)  # cool down to help with detecting events properly


@pytest.mark.bot
async def test_no_emote(ctx: BaseContext):
    await ctx.send(":pssh2doesnotexist:")

    def check(m: MessageCreate):
        return m.message.author.id == ctx.bot.user.id

    # Wait for bot to send message
    msg_event: MessageCreate = await ctx.bot.wait_for(
        "message_create", checks=check, timeout=5
    )

    error_msg = msg_event.message
    embed = error_msg.embeds[0]
    assert embed.title == "Emote not found."
    assert (
        embed.footer.text
        == "Emotes with a 60%+ similarity are included in suggestions"
    )
