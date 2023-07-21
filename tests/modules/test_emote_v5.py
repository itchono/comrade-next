import pytest
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.lib.testing_utils import (
    wait_for_message_or_fetch,
)


@pytest.mark.bot
@pytest.mark.parametrize("emote", ("pssh", "PSSH", " pssh "))
async def test_sending_emote(prefixed_ctx: PrefixedContext, emote: str):
    """
    Tests sending an emote from the bot,
    with both case-sensitive and case-insensitive emote names.
    """
    await prefixed_ctx.send(f":{emote}:")

    def check(m: MessageCreate):
        return (
            m.message.webhook_id is not None
            and m.message.channel == prefixed_ctx.channel
        )

    emoji_msg = await wait_for_message_or_fetch(prefixed_ctx, check, timeout=10)

    assert (
        emoji_msg.content
        == "https://cdn.discordapp.com/attachments/810726667026300958/810732433460559872/pssh.png"
    )


@pytest.mark.bot
async def test_no_emote(prefixed_ctx: PrefixedContext):
    await prefixed_ctx.send(":pssh2doesnotexist:")

    def check(m: MessageCreate):
        return (
            m.message.author == prefixed_ctx.bot.user
            and m.message.channel == prefixed_ctx.channel
        )

    error_msg = await wait_for_message_or_fetch(prefixed_ctx, check, timeout=10)
    embed = error_msg.embeds[0]
    assert embed.title == "Emote not found."
    assert (
        embed.footer.text
        == "Emotes with a 60%+ similarity are included in suggestions"
    )
