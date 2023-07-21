import pytest
from interactions.api.events import MessageCreate
from interactions.ext.prefixed_commands import PrefixedContext

from comrade.core.comrade_client import Comrade
from comrade.lib.testing_utils import (
    CapturingContext,
    wait_for_message_or_fetch,
)
from comrade.modules.emote_system import EmoteSystem


@pytest.fixture(scope="module")
async def emotesystem_ext(bot: Comrade) -> EmoteSystem:
    return bot.get_ext("EmoteSystem")


@pytest.mark.bot
@pytest.mark.parametrize("emote", ("pssh", "PSSH", " pssh "))
async def test_sending_emote(
    offline_ctx: CapturingContext, emotesystem_ext: EmoteSystem, emote: str
):
    """
    Tests sending an emote from the bot,
    with both case-sensitive and case-insensitive emote names.
    """

    # create a send message event
    await offline_ctx.send(f":{emote}:")
    emote_msg_event = MessageCreate(offline_ctx.captured_message)

    # call the listener
    await emotesystem_ext.emote_listener.callback(
        emotesystem_ext, emote_msg_event
    )

    def check(m: MessageCreate):
        return (
            m.message.webhook_id is not None
            and m.message.channel == offline_ctx.channel
        )

    emoji_msg = await wait_for_message_or_fetch(offline_ctx, check, timeout=2)

    assert (
        emoji_msg.content
        == "https://cdn.discordapp.com/attachments/810726667026300958/810732433460559872/pssh.png"
    )


@pytest.mark.bot
async def test_no_emote(
    offline_ctx: PrefixedContext, emotesystem_ext: EmoteSystem
):
    # create a send message event
    await offline_ctx.send(":pssh2doesnotexist:")
    emote_msg_event = MessageCreate(offline_ctx.captured_message)

    # call the listener
    await emotesystem_ext.emote_listener.callback(
        emotesystem_ext, emote_msg_event
    )

    def check(m: MessageCreate):
        return (
            m.message.author == offline_ctx.bot.user
            and m.message.channel == offline_ctx.channel
        )

    error_msg = await wait_for_message_or_fetch(offline_ctx, check, timeout=2)
    embed = error_msg.embeds[0]
    assert embed.title == "Emote not found."
    assert (
        embed.footer.text
        == "Emotes with a 60%+ similarity are included in suggestions"
    )
