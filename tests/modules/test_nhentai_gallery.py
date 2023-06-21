import pytest
from interactions import BaseContext, InteractionCommand

from comrade.core.configuration import TEST_GUILD_ID


@pytest.mark.bot
async def test_gallery_start(ctx: BaseContext):
    nhentai_gallery_cmd: InteractionCommand = ctx.bot.interactions_by_scope[
        TEST_GUILD_ID
    ]["nhentai gallery"]

    await nhentai_gallery_cmd.callback(ctx, 266745)

    # Get latest message in channel
    start_embed_msg = (await ctx.channel.fetch_messages(limit=1))[0]
    assert (
        start_embed_msg.content
        == "Type `np` (or click the button) to start reading, and advance pages."
    )

    start_embed = start_embed_msg.embeds[0]

    assert start_embed.title == "Upload duplicate, replace with white page"
    assert start_embed.url == "https://nhentai.net/g/266745/"
    assert start_embed.footer.text == "Found using nhentai.to Mirror"
